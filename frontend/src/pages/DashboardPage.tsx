import React, { useState, useEffect } from 'react';
import {
  Row,
  Col,
  Card,
  Statistic,
  Progress,
  List,
  Typography,
  Tag,
  Space,
  Button,
  Empty,
  Spin,
  Alert,
} from 'antd';
import {
  UnorderedListOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  ExclamationCircleOutlined,
  ReloadOutlined,
  PlayCircleOutlined,
  FileTextOutlined,
  RobotOutlined,
} from '@ant-design/icons';
import { systemApi } from '../services/api';
import { eventBus } from '../utils/eventBus';
import type { Task } from '../types';

const { Title, Text } = Typography;

interface DashboardStats {
  totalTasks: number;
  completedTasks: number;
  runningTasks: number;
  pendingTasks: number;
  errorTasks: number;
}

const DashboardPage: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats>({
    totalTasks: 0,
    completedTasks: 0,
    runningTasks: 0,
    pendingTasks: 0,
    errorTasks: 0,
  });
  const [recentTasks, setRecentTasks] = useState<Task[]>([]);
  const [systemHealth, setSystemHealth] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadDashboardData();

    // Set up EventBus listeners for real-time updates
    const handleTaskUpdate = (data: any) => {
      console.log('Task update received:', data);
      refreshStats();
    };

    const unsubTaskUpdate = eventBus.on('task:updated', handleTaskUpdate);
    const unsubStepUpdate = eventBus.on('task:stepUpdated', handleTaskUpdate);

    return () => {
      unsubTaskUpdate();
      unsubStepUpdate();
    };
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);

      // Load dashboard stats and system health in parallel
      const [dashboardStats, health] = await Promise.all([
        systemApi.getDashboardStats(),
        systemApi
          .getHealth()
          .catch(() => ({ status: 'unknown', version: 'unknown' })),
      ]);

      // Set statistics from the API response
      setStats({
        totalTasks: dashboardStats.total_tasks,
        completedTasks: dashboardStats.completed_tasks,
        runningTasks: dashboardStats.running_tasks,
        pendingTasks: dashboardStats.pending_tasks,
        errorTasks: dashboardStats.error_tasks,
      });

      // Convert recent activity to tasks format
      const recentTasksFromActivity = dashboardStats.recent_activity.map(
        (activity: any) => ({
          id: activity.task_id,
          title: activity.task_title,
          description: '', // Not provided in activity
          status: activity.status,
          createdAt: activity.created_at,
          completedAt: activity.completed_at,
          complexity: 'medium', // Default value
          mode: 'auto', // Default value
        })
      );

      setRecentTasks(recentTasksFromActivity);
      setSystemHealth(health);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const refreshStats = async () => {
    try {
      setRefreshing(true);
      const dashboardStats = await systemApi.getDashboardStats();

      const newStats: DashboardStats = {
        totalTasks: dashboardStats.total_tasks,
        completedTasks: dashboardStats.completed_tasks,
        runningTasks: dashboardStats.running_tasks,
        pendingTasks: dashboardStats.pending_tasks,
        errorTasks: dashboardStats.error_tasks,
      };

      setStats(newStats);

      // Convert recent activity to tasks format
      const recentTasksFromActivity = dashboardStats.recent_activity.map(
        (activity: any) => ({
          id: activity.task_id,
          title: activity.task_title,
          description: '',
          status: activity.status,
          createdAt: activity.created_at,
          completedAt: activity.completed_at,
          complexity: 'medium',
          mode: 'auto',
        })
      );

      setRecentTasks(recentTasksFromActivity);
    } catch (error) {
      console.error('Error refreshing stats:', error);
    } finally {
      setRefreshing(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircleOutlined style={{ color: '#52c41a' }} />;
      case 'running':
        return <PlayCircleOutlined style={{ color: '#1890ff' }} />;
      case 'pending':
        return <ClockCircleOutlined style={{ color: '#faad14' }} />;
      case 'error':
        return <ExclamationCircleOutlined style={{ color: '#ff4d4f' }} />;
      default:
        return <ClockCircleOutlined style={{ color: '#d9d9d9' }} />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'running':
        return 'processing';
      case 'pending':
        return 'warning';
      case 'error':
        return 'error';
      default:
        return 'default';
    }
  };

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const completionPercentage =
    stats.totalTasks > 0
      ? Math.round((stats.completedTasks / stats.totalTasks) * 100)
      : 0;

  if (loading) {
    return (
      <div style={{ textAlign: 'center', marginTop: '20%' }}>
        <Spin size='large' />
        <div style={{ marginTop: 16 }}>
          <Text>Carregando dashboard...</Text>
        </div>
      </div>
    );
  }

  return (
    <div style={{ padding: '24px' }}>
      <div
        style={{
          marginBottom: '24px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}
      >
        <Title level={2} style={{ margin: 0 }}>
          Dashboard OpenManus
        </Title>
        <Button
          icon={<ReloadOutlined />}
          onClick={loadDashboardData}
          loading={refreshing}
        >
          Atualizar
        </Button>
      </div>

      {/* System Health Alert */}
      {systemHealth && (
        <Alert
          message={`Sistema ${
            systemHealth.status === 'healthy' ? 'Online' : 'Offline'
          }`}
          description={`Versão: ${systemHealth.version} | Status: ${systemHealth.status}`}
          type={systemHealth.status === 'healthy' ? 'success' : 'error'}
          showIcon
          style={{ marginBottom: '24px' }}
        />
      )}

      {/* Statistics Cards */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title='Total de Tarefas'
              value={stats.totalTasks}
              prefix={<UnorderedListOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title='Concluídas'
              value={stats.completedTasks}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title='Em Execução'
              value={stats.runningTasks}
              prefix={<PlayCircleOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title='Pendentes'
              value={stats.pendingTasks}
              prefix={<ClockCircleOutlined />}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        {/* Progress Overview */}
        <Col xs={24} lg={8}>
          <Card
            title={
              <Space>
                <RobotOutlined />
                <span>Progresso Geral</span>
              </Space>
            }
          >
            <div style={{ textAlign: 'center' }}>
              <Progress
                type='circle'
                percent={completionPercentage}
                format={() => `${completionPercentage}%`}
                size={120}
              />
              <div style={{ marginTop: '16px' }}>
                <Text type='secondary'>
                  {stats.completedTasks} de {stats.totalTasks} tarefas
                  concluídas
                </Text>
              </div>
            </div>

            {stats.errorTasks > 0 && (
              <div style={{ marginTop: '16px', textAlign: 'center' }}>
                <Tag color='error'>{stats.errorTasks} tarefa(s) com erro</Tag>
              </div>
            )}
          </Card>
        </Col>

        {/* Recent Tasks */}
        <Col xs={24} lg={16}>
          <Card
            title={
              <Space>
                <FileTextOutlined />
                <span>Tarefas Recentes</span>
              </Space>
            }
          >
            {recentTasks.length === 0 ? (
              <Empty
                description='Nenhuma tarefa encontrada'
                style={{ margin: '20px 0' }}
              />
            ) : (
              <List
                dataSource={recentTasks}
                renderItem={(task) => (
                  <List.Item>
                    <List.Item.Meta
                      avatar={getStatusIcon(task.status)}
                      title={
                        <Space>
                          <span>{task.title}</span>
                          <Tag color={getStatusColor(task.status)}>
                            {task.status.toUpperCase()}
                          </Tag>
                        </Space>
                      }
                      description={
                        <div>
                          <Text
                            ellipsis
                            style={{ display: 'block', marginBottom: '4px' }}
                          >
                            {task.description}
                          </Text>
                          <Text type='secondary' style={{ fontSize: '12px' }}>
                            Criada em: {formatTime(task.createdAt)}
                            {task.completedAt && (
                              <>
                                {' '}
                                • Concluída em: {formatTime(task.completedAt)}
                              </>
                            )}
                          </Text>
                        </div>
                      }
                    />
                  </List.Item>
                )}
              />
            )}
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default DashboardPage;
