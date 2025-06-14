import asyncio
from collections.abc import Hashable
import json
from pathlib import Path
from typing import Any, ClassVar

import pandas as pd

from app.compat import Field, model_validator
from app.core.settings import settings
from app.llm import LLM
from app.logger import logger
from app.tool.base import BaseTool


class DataVisualization(BaseTool):
    name: str = "data_visualization"
    description: str = """Visualize statistical chart or Add insights in chart with JSON info from visualization_preparation tool. You can do steps as follows:
1. Visualize statistical chart
2. Choose insights into chart based on step 1 (Optional)
Outputs:
1. Charts (png/html)
2. Charts Insights (.md)(Optional)"""
    parameters: ClassVar[dict] = {
        "type": "object",
        "properties": {
            "json_path": {
                "type": "string",
                "description": """file path of json info with ".json" in the end""",
            },
            "output_type": {
                "description": "Rendering format (html=interactive)",
                "type": "string",
                "default": "html",
                "enum": ["png", "html"],
            },
            "tool_type": {
                "description": "visualize chart or add insights",
                "type": "string",
                "default": "visualization",
                "enum": ["visualization", "insight"],
            },
            "language": {
                "description": "english(en) / chinese(zh)",
                "type": "string",
                "default": "en",
                "enum": ["zh", "en"],
            },
        },
        "required": ["json_path"],
    }
    llm: LLM = Field(default_factory=LLM, description="Language model instance")

    @model_validator(mode="after")
    def initialize_llm(self):
        """Initialize llm with default settings if not provided."""
        if self.llm is None or not isinstance(self.llm, LLM):
            self.llm = LLM(config_name=self.name.lower())
        return self

    def get_file_path(
        self,
        json_info: list[dict[str, str]],
        path_str: str,
        directory: str | None = None,
    ) -> list[str]:
        res = []
        for item in json_info:
            if Path(item[path_str]).exists():
                res.append(item[path_str])
            elif Path(f"{directory or settings.workspace_root}" / item[path_str]).exists():
                res.append(str(Path(f"{directory or settings.workspace_root}") / item[path_str]))
            else:
                raise Exception(f"No such file or directory: {item[path_str]}")
        return res

    def success_output_template(self, result: list[dict[str, str]]) -> str:
        content = ""
        if len(result) == 0:
            return "Is EMPTY!"
        for item in result:
            content += f"""## {item["title"]}\nChart saved in: {item["chart_path"]}"""
            if "insight_path" in item and item["insight_path"] and "insight_md" in item:
                content += "\n" + item["insight_md"]
            else:
                content += "\n"
        return f"Chart Generated Successful!\n{content}"

    async def data_visualization(self, json_info: list[dict[str, str]], output_type: str, language: str) -> str:
        data_list = []
        csv_file_path = self.get_file_path(json_info, "csvFilePath")
        for index, item in enumerate(json_info):
            df = pd.read_csv(csv_file_path[index], encoding="utf-8")
            df = df.astype(object)
            df = df.where(pd.notnull(df), None)
            data_dict_list = df.to_json(orient="records", force_ascii=False)

            data_list.append(
                {
                    "file_name": Path(csv_file_path[index]).name.replace(".csv", ""),
                    "dict_data": data_dict_list,
                    "chartTitle": item["chartTitle"],
                }
            )
        tasks = [
            self.invoke_vmind(
                dict_data=item["dict_data"],
                chart_description=item["chartTitle"],
                file_name=item["file_name"],
                output_type=output_type,
                task_type="visualization",
                language=language,
            )
            for item in data_list
        ]

        results = await asyncio.gather(*tasks)
        error_list = []
        success_list = []
        for index, result in enumerate(results):
            csv_path = csv_file_path[index]
            if "error" in result and "chart_path" not in result:
                error_list.append(f"Error in {csv_path}: {result['error']}")
            else:
                success_list.append(
                    {
                        **result,
                        "title": json_info[index]["chartTitle"],
                    }
                )
        if len(error_list) > 0:
            return {
                "observation": f"# Error chart generated{'\n'.join(error_list)}\n{self.success_output_template(success_list)}",
                "success": False,
            }
        return {"observation": f"{self.success_output_template(success_list)}"}

    async def add_insighs(self, json_info: list[dict[str, str]], output_type: str) -> str:
        data_list = []
        chart_file_path = self.get_file_path(
            json_info,
            "chartPath",
            str(Path(settings.workspace_root) / "visualization"),
        )
        for index, item in enumerate(json_info):
            if "insights_id" in item:
                data_list.append(
                    {
                        "file_name": Path(chart_file_path[index]).name.replace(f".{output_type}", ""),
                        "insights_id": item["insights_id"],
                    }
                )
        tasks = [
            self.invoke_vmind(
                insights_id=item["insights_id"],
                file_name=item["file_name"],
                output_type=output_type,
                task_type="insight",
            )
            for item in data_list
        ]
        results = await asyncio.gather(*tasks)
        error_list = []
        success_list = []
        for index, result in enumerate(results):
            chart_path = chart_file_path[index]
            if "error" in result and "chart_path" not in result:
                error_list.append(f"Error in {chart_path}: {result['error']}")
            else:
                success_list.append(chart_path)
        success_template = f"# Charts Update with Insights\n{','.join(success_list)}" if len(success_list) > 0 else ""
        if len(error_list) > 0:
            return {
                "observation": f"# Error in chart insights:{'\n'.join(error_list)}\n{success_template}",
                "success": False,
            }
        return {"observation": f"{success_template}"}

    async def execute(
        self,
        json_path: str,
        output_type: str | None = "html",
        tool_type: str | None = "visualization",
        language: str | None = "en",
    ) -> str:
        try:
            logger.info(f"📈 data_visualization with {json_path} in: {tool_type} ")
            with Path(json_path).open(encoding="utf-8") as file:
                json_info = json.load(file)
            if tool_type == "visualization":
                return await self.data_visualization(json_info, output_type, language)
            return await self.add_insighs(json_info, output_type)
        except Exception as e:
            return {
                "observation": f"Error: {e}",
                "success": False,
            }

    async def invoke_vmind(
        self,
        file_name: str,
        output_type: str,
        task_type: str,
        insights_id: list[str] | None = None,
        dict_data: list[dict[Hashable, Any]] | None = None,
        chart_description: str | None = None,
        language: str = "en",
    ):
        llm_config = {
            "base_url": self.llm.base_url,
            "model": self.llm.model,
            "api_key": self.llm.api_key,
        }
        vmind_params = {
            "llm_config": llm_config,
            "user_prompt": chart_description,
            "dataset": dict_data,
            "file_name": file_name,
            "output_type": output_type,
            "insights_id": insights_id,
            "task_type": task_type,
            "directory": str(settings.workspace_root),
            "language": language,
        }
        # build async sub process
        process = await asyncio.create_subprocess_exec(
            "npx",
            "ts-node",
            "src/chartVisualize.ts",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=Path(__file__).parent,
        )
        input_json = json.dumps(vmind_params, ensure_ascii=False).encode("utf-8")
        try:
            stdout, stderr = await process.communicate(input_json)
            stdout_str = stdout.decode("utf-8")
            stderr_str = stderr.decode("utf-8")
            if process.returncode == 0:
                return json.loads(stdout_str)
            return {"error": f"Node.js Error: {stderr_str}"}
        except Exception as e:
            return {"error": f"Subprocess Error: {e!s}"}
