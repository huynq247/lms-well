import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { 
  LayoutDashboard, 
  Users, 
  BookOpen, 
  FileText, 
  ClipboardList,
  GraduationCap,
  LogOut,
  Menu
} from 'lucide-react';
import { useState } from 'react';

interface MenuItem {
  title: string;
  path: string;
  icon: any;
  roles: string[];
}

export default function AdminLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const menuItems: MenuItem[] = [
    { title: 'Dashboard', path: '/admin/dashboard', icon: LayoutDashboard, roles: ['ADMIN', 'TEACHER'] },
    { title: 'User Management', path: '/admin/users', icon: Users, roles: ['ADMIN'] },
    { title: 'Courses', path: '/admin/courses', icon: BookOpen, roles: ['ADMIN', 'TEACHER'] },
    { title: 'Lessons', path: '/admin/lessons', icon: FileText, roles: ['ADMIN', 'TEACHER'] },
    { title: 'Flashcards', path: '/admin/decks', icon: GraduationCap, roles: ['ADMIN', 'TEACHER'] },
    { title: 'Assignments', path: '/admin/assignments', icon: ClipboardList, roles: ['ADMIN', 'TEACHER'] },
  ];

  // Filter menu items based on user role
  const filteredMenuItems = menuItems.filter(item => 
    item.roles.includes(user?.role?.toUpperCase() || '')
  );

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <aside className={`${sidebarOpen ? 'w-64' : 'w-20'} bg-gray-900 text-white transition-all duration-300 flex flex-col`}>
        {/* Logo/Title */}
        <div className="p-4 border-b border-gray-800 flex items-center justify-between">
          {sidebarOpen && (
            <h1 className="text-xl font-bold">🎓 LMS Admin</h1>
          )}
          <button 
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 hover:bg-gray-800 rounded"
          >
            <Menu size={20} />
          </button>
        </div>

        {/* Navigation Menu */}
        <nav className="flex-1 py-4 overflow-y-auto">
          {filteredMenuItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            
            return (
              <button
                key={item.path}
                onClick={() => navigate(item.path)}
                className={`w-full flex items-center gap-3 px-4 py-3 hover:bg-gray-800 transition-colors ${
                  isActive ? 'bg-gray-800 border-l-4 border-blue-500' : ''
                }`}
              >
                <Icon size={20} />
                {sidebarOpen && (
                  <span className="font-medium">{item.title}</span>
                )}
              </button>
            );
          })}
        </nav>

        {/* User Info at Bottom */}
        {sidebarOpen && user && (
          <div className="p-4 border-t border-gray-800">
            <div className="text-sm">
              <div className="font-semibold">{user.full_name || user.username}</div>
              <div className="text-gray-400 text-xs">{user.role}</div>
            </div>
          </div>
        )}
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">
              {menuItems.find(item => item.path === location.pathname)?.title || 'Admin Panel'}
            </h2>
          </div>
          
          <div className="flex items-center gap-4">
            <div className="text-right">
              <div className="text-sm font-medium text-gray-900">
                {user?.full_name || user?.username}
              </div>
              <div className="text-xs text-gray-500">{user?.role}</div>
            </div>
            <Button 
              onClick={handleLogout}
              variant="destructive"
              size="sm"
              className="gap-2"
            >
              <LogOut size={16} />
              Logout
            </Button>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
