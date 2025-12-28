// client/src/scenes/navbar/index.jsx (UPDATED)
import { useState } from "react";
import { 
  Search, 
  MessageSquare, 
  Sun, 
  Moon, 
  Menu, 
  X, 
  Users, 
  ChevronDown,
  LogOut,
  User,
  Home,
  Bell
} from "lucide-react";
import { useDispatch, useSelector } from "react-redux";
import { setMode, setLogout } from "state";
import { useNavigate, useLocation } from "react-router-dom";
import FlexBetween from "components/FlexBetween";
import SearchUsers from "components/SearchUsers";
import ChatInterface from "components/ChatInterface";
import NotificationBell from "components/NotificationBell";
import NotificationCenter from "components/NotificationCenter";

const Navbar = () => {
  const [isMobileMenuToggled, setIsMobileMenuToggled] = useState(false);
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [isChatOpen, setIsChatOpen] = useState(false);
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const location = useLocation();
  const user = useSelector((state) => state.user);
  const mode = useSelector((state) => state.mode);
  const fullName = user ? `${user.firstName} ${user.lastName}` : "";

  const navItems = [
    { icon: Home, label: "Home", path: "/home" },
    { icon: Users, label: "My Network", path: "/home/alumniPage" },
    { icon: MessageSquare, label: "Messaging", onClick: () => setIsChatOpen(true) },
  ];

  return (
    <>
      <nav className="sticky top-0 z-50 w-full bg-white/95 dark:bg-slate-800/95 backdrop-blur-md border-b border-slate-200/50 dark:border-slate-700/50 shadow-lg transition-all duration-300">
        <div className="max-w-7xl mx-auto px-4 lg:px-[6%] h-16 flex items-center justify-between">
          {/* Left: Logo and Search */}
          <div className="flex items-center gap-4 flex-1">
            <h1
              onClick={() => navigate("/home")}
              className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent cursor-pointer flex-shrink-0"
            >
              Uni<span className="text-white bg-gradient-to-r from-blue-600 to-indigo-600 px-2 py-0.5 rounded-lg ml-0.5 font-bold">Link</span>
            </h1>
            
            <div className="relative max-w-xs w-full hidden md:block">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Search className="h-4 w-4 text-slate-400" />
              </div>
              <input
                type="text"
                placeholder="Search professionals"
                onClick={() => setIsSearchOpen(true)}
                className="block w-full pl-10 pr-4 py-2.5 bg-slate-100 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-full text-sm placeholder-slate-500 dark:placeholder-slate-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent focus:bg-white dark:focus:bg-slate-800 transition-all duration-200 outline-none"
              />
            </div>
          </div>

          {/* Right: Navigation Items */}
          <div className="flex items-center gap-0 md:gap-2">
            {navItems.map((item) => (
              <button
                key={item.label}
                onClick={item.onClick || (() => navigate(item.path))}
                className={`flex flex-col items-center justify-center px-3 py-2 rounded-lg transition-all relative group ${
                  location.pathname === item.path 
                    ? 'bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400' 
                    : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700 hover:text-slate-900 dark:hover:text-white'
                }`}
              >
                <item.icon className="h-5 w-5" />
                <span className="text-[10px] mt-0.5 hidden lg:block font-medium">{item.label}</span>
              </button>
            ))}

            <div className="hidden md:flex items-center gap-2 pl-4 border-l border-slate-200 dark:border-slate-700 ml-4">
              <button
                onClick={() => dispatch(setMode())}
                className="p-2.5 text-slate-600 hover:bg-slate-100 dark:hover:bg-slate-700 dark:text-slate-400 rounded-lg transition-colors"
              >
                {mode === "dark" ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
              </button>
              
              <NotificationBell />

              <div className="relative">
                <button
                  onClick={() => setIsProfileOpen(!isProfileOpen)}
                  className="flex flex-col items-center text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 px-2 py-1.5 transition-colors"
                >
                  <div className="h-6 w-6 rounded-full bg-gradient-to-br from-blue-400 to-indigo-400 overflow-hidden border border-blue-300">
                    <img src={user?.picturePath} alt="Me" className="w-full h-full object-cover" />
                  </div>
                  <div className="flex items-center text-[10px] mt-0.5 font-medium">
                    <ChevronDown className="h-3 w-3" />
                  </div>
                </button>

                {isProfileOpen && (
                  <div className="absolute right-0 mt-2 w-72 bg-white dark:bg-slate-800 rounded-xl shadow-2xl border border-slate-200/50 dark:border-slate-700/50 py-4 z-50 backdrop-blur-sm">
                    <div className="px-4 pb-4 border-b border-slate-200 dark:border-slate-700 flex items-center gap-3">
                      <div className="h-12 w-12 rounded-full bg-gradient-to-br from-blue-400 to-indigo-400 overflow-hidden border-2 border-blue-300">
                        <img src={user?.picturePath} alt="Profile" className="w-full h-full object-cover" />
                      </div>
                      <div>
                        <p className="font-semibold text-sm leading-tight text-slate-900 dark:text-white">{fullName}</p>
                        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">{user?.Year} student</p>
                      </div>
                    </div>
                    <button
                      onClick={() => {
                        setIsProfileOpen(false);
                        navigate(`/profile/${user._id}`);
                      }}
                      className="w-full px-4 py-2.5 mt-2 text-left text-sm font-semibold text-blue-600 dark:text-blue-400 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors"
                    >
                      View Profile
                    </button>
                    <button
                      onClick={() => dispatch(setLogout())}
                      className="w-full px-4 py-2 text-left text-sm text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors"
                    >
                      Sign Out
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Mobile Search/Menu Toggle */}
          <div className="md:hidden flex items-center gap-2">
             <button onClick={() => setIsSearchOpen(true)} className="p-2.5 text-slate-600 hover:bg-slate-100 dark:hover:bg-slate-700 dark:text-slate-400 rounded-lg transition-colors"><Search className="h-5 w-5"/></button>
             <button onClick={() => setIsMobileMenuToggled(!isMobileMenuToggled)} className="p-2.5 text-slate-600 hover:bg-slate-100 dark:hover:bg-slate-700 dark:text-slate-400 rounded-lg transition-colors"><Menu className="h-5 w-5"/></button>
          </div>
        </div>
      </nav>

      {/* Modals & Overlays */}
      <SearchUsers isOpen={isSearchOpen} onClose={() => setIsSearchOpen(false)} />
      <ChatInterface isOpen={isChatOpen} onClose={() => setIsChatOpen(false)} />
      <NotificationCenter />
    </>
  );
};

export default Navbar;