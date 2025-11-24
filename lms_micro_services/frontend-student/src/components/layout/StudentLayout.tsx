import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { 
  BookOpen, 
  ClipboardList,
  GraduationCap,
  Brain,
  BarChart,
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

export default function StudentLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const menuItems: MenuItem[] = [
    { title: 'My Courses', path: '/student/courses', icon: BookOpen, roles: ['STUDENT'] },
    { title: 'My Assignments', path: '/student/assignments', icon: ClipboardList, roles: ['STUDENT'] },
    { title: 'Flashcards', path: '/student/decks', icon: Brain, roles: ['STUDENT'] },
    { title: 'Progress', path: '/student/progress', icon: BarChart, roles: ['STUDENT'] },
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
      <aside className={`${sidebarOpen ? 'w-64' : 'w-20'} bg-indigo-900 text-white transition-all duration-300 flex flex-col`}>
        {/* Logo/Title */}
        <div className="p-4 flex items-center justify-between border-b border-indigo-800">
          {sidebarOpen && (
            <div className="flex items-center gap-2">
              <GraduationCap size={28} />
              <span className="font-bold text-lg">LMS Student</span>
            </div>
          )}
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="text-white hover:bg-indigo-800"
          >
            <Menu size={20} />
          </Button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-2">
          {filteredMenuItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            
            return (
              <button
                key={item.path}
                onClick={() => navigate(item.path)}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                  isActive 
                    ? 'bg-indigo-800 text-white shadow-lg' 
                    : 'text-indigo-100 hover:bg-indigo-800/50'
                } ${!sidebarOpen && 'justify-center'}`}
              >
                <Icon size={20} />
                {sidebarOpen && <span className="font-medium">{item.title}</span>}
              </button>
            );
          })}
        </nav>

        {/* User Info & Logout */}
        <div className="p-4 border-t border-indigo-800">
          {sidebarOpen ? (
            <div className="space-y-3">
              <div className="text-sm">
                <div className="font-semibold">{user?.full_name}</div>
                <div className="text-indigo-300 text-xs">{user?.email}</div>
                <div className="text-indigo-400 text-xs mt-1">
                  Role: {user?.role}
                </div>
              </div>
              <Button
                onClick={handleLogout}
                variant="ghost"
                className="w-full justify-start text-white hover:bg-indigo-800 gap-2"
              >
                <LogOut size={18} />
                Logout
              </Button>
            </div>
          ) : (
            <Button
              onClick={handleLogout}
              variant="ghost"
              size="icon"
              className="w-full text-white hover:bg-indigo-800"
            >
              <LogOut size={20} />
            </Button>
          )}
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="bg-white shadow-sm border-b border-gray-200 px-8 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-gray-800">
              {filteredMenuItems.find(item => item.path === location.pathname)?.title || 'Dashboard'}
            </h1>
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-600">Welcome, {user?.full_name}!</span>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
