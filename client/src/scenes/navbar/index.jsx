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
      <nav className="sticky top-0 z-50 w-full bg-white dark:bg-grey-800 border-b border-grey-200 dark:border-grey-700 shadow-sm transition-all duration-300">
        <div className="max-w-7xl mx-auto px-4 lg:px-[6%] h-14 flex items-center justify-between">
          {/* Left: Logo and Search */}
          <div className="flex items-center gap-2 flex-1">
            <h1
              onClick={() => navigate("/home")}
              className="text-2xl font-bold text-primary-500 cursor-pointer flex-shrink-0"
            >
              Uni<span className="bg-primary-500 text-white px-1 rounded-sm ml-0.5">L</span>
            </h1>
            
            <div className="relative max-w-xs w-full hidden md:block">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Search className="h-4 w-4 text-grey-500" />
              </div>
              <input
                type="text"
                placeholder="Search"
                onClick={() => setIsSearchOpen(true)}
                className="block w-full pl-10 pr-3 py-1.5 bg-primary-50 dark:bg-grey-700 border-none rounded-md text-sm placeholder-grey-500 focus:ring-2 focus:ring-primary-500 focus:bg-white dark:focus:bg-grey-600 transition-all duration-200 outline-none"
              />
            </div>
          </div>

          {/* Right: Navigation Items */}
          <div className="flex items-center gap-1 md:gap-6">
            {navItems.map((item) => (
              <button
                key={item.label}
                onClick={item.onClick || (() => navigate(item.path))}
                className={`flex flex-col items-center justify-center px-2 py-1 transition-colors relative group ${
                  location.pathname === item.path ? 'text-grey-900 dark:text-white' : 'text-grey-500 dark:text-grey-400 hover:text-grey-900 dark:hover:text-white'
                }`}
              >
                <item.icon className="h-6 w-6" />
                <span className="text-[10px] mt-0.5 hidden lg:block">{item.label}</span>
                {location.pathname === item.path && (
                  <div className="absolute bottom-[-14px] left-0 right-0 h-0.5 bg-grey-900 dark:bg-white" />
                )}
              </button>
            ))}

            <div className="hidden md:flex items-center gap-4 pl-4 border-l border-grey-200 dark:border-grey-700 ml-2">
              <button
                onClick={() => dispatch(setMode())}
                className="p-2 text-grey-500 hover:bg-grey-100 dark:hover:bg-grey-700 rounded-full transition-colors"
              >
                {mode === "dark" ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
              </button>
              
              <NotificationBell />

              <div className="relative">
                <button
                  onClick={() => setIsProfileOpen(!isProfileOpen)}
                  className="flex flex-col items-center text-grey-500 hover:text-grey-900 dark:hover:text-white"
                >
                  <div className="h-6 w-6 rounded-full bg-grey-200 overflow-hidden">
                    <img src={user?.picturePath} alt="Me" className="w-full h-full object-cover" />
                  </div>
                  <div className="flex items-center text-[10px] mt-0.5">
                    Me <ChevronDown className="h-3 w-3 ml-0.5" />
                  </div>
                </button>

                {isProfileOpen && (
                  <div className="absolute right-0 mt-2 w-64 bg-white dark:bg-grey-800 rounded-lg shadow-xl border border-grey-200 dark:border-grey-700 py-4 z-50">
                    <div className="px-4 pb-4 border-b border-grey-200 dark:border-grey-700 flex items-center gap-3">
                      <div className="h-12 w-12 rounded-full bg-grey-200 overflow-hidden">
                        <img src={user?.picturePath} alt="Profile" className="w-full h-full object-cover" />
                      </div>
                      <div>
                        <p className="font-semibold text-sm leading-tight">{fullName}</p>
                        <p className="text-xs text-grey-500 mt-1">{user?.Year} student</p>
                      </div>
                    </div>
                    <button
                      onClick={() => {
                        setIsProfileOpen(false);
                        navigate(`/profile/${user._id}`);
                      }}
                      className="w-full px-4 py-2 mt-2 text-left text-sm font-semibold text-primary-500 hover:bg-grey-50 dark:hover:bg-grey-700 transition-colors"
                    >
                      View Profile
                    </button>
                    <button
                      onClick={() => dispatch(setLogout())}
                      className="w-full px-4 py-2 text-left text-sm text-grey-500 hover:bg-grey-50 dark:hover:bg-grey-700 transition-colors"
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
             <button onClick={() => setIsSearchOpen(true)} className="p-2 text-grey-500"><Search className="h-6 w-6"/></button>
             <button onClick={() => setIsMobileMenuToggled(!isMobileMenuToggled)} className="p-2 text-grey-500"><Menu className="h-6 w-6"/></button>
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