import {
    // ...existing imports...
    BookOutlined,
} from '@ant-design/icons';

// ...existing code...

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
    // ...existing code...

    const menuItems = [
        // ...existing menu items...
        {
            key: '/knowledge',
            icon: <BookOutlined />,
            label: <Link to="/knowledge">Knowledge</Link>,
        },
        // ...existing code...
    ];

    // ...existing code...
};

// ...existing code...
