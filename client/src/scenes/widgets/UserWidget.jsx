import { 
  Settings, 
  MapPin, 
  GraduationCap, 
  Settings2,
  Bell,
  Eye,
  BarChart3
} from "lucide-react";
import UserImage from "components/UserImage";
import FlexBetween from "components/FlexBetween";
import WidgetWrapper from "components/WidgetWrapper";
import NotificationSettings from "components/NotificationSettings";
import { useSelector } from "react-redux";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { API_ENDPOINTS } from "config/api";
import { motion } from "framer-motion";

const UserWidget = ({ userId, picturePath }) => {
  const [user, setUserData] = useState(null);
  const navigate = useNavigate();
  const token = useSelector((state) => state.token);
  const loggedInUserId = useSelector((state) => state.user?._id);
  const isOwnProfile = userId === loggedInUserId;
  const [showSettings, setShowSettings] = useState(false);

  const getUser = async () => {
    const response = await fetch(API_ENDPOINTS.USER_BY_ID(userId), {
      method: "GET",
      headers: { Authorization: `Bearer ${token}` },
    });
    const data = await response.json();
    setUserData(data);
  };

  useEffect(() => {
    getUser();
  }, [userId]); // eslint-disable-line react-hooks/exhaustive-deps

  if (!user) return null;

  const { firstName, lastName, location, Year, viewedProfile, impressions } = user;

  return (
    <>
      <WidgetWrapper className="linkedin-card overflow-hidden !p-0">
        {/* Background Banner */}
        <div className="h-16 bg-gradient-to-r from-primary-400 to-primary-600 w-full relative" />
        
        <div className="px-4 pb-4">
          {/* Profile Info */}
          <div className="flex flex-col items-center -mt-8 mb-4">
            <motion.div
              whileHover={{ scale: 1.05 }}
              className="relative cursor-pointer"
              onClick={() => navigate(`/profile/${userId}`)}
            >
              <UserImage 
                image={picturePath} 
                size="72px" 
                className="border-4 border-white dark:border-grey-800 shadow-sm rounded-full" 
              />
            </motion.div>
            <h4 
              className="text-lg font-bold text-grey-800 dark:text-grey-100 mt-2 hover:underline cursor-pointer"
              onClick={() => navigate(`/profile/${userId}`)}
            >
              {firstName} {lastName}
            </h4>
            <p className="text-xs text-grey-500 dark:text-grey-400 text-center px-4">
              {Year} student at UniLink Community
            </p>
          </div>

          <div className="border-t border-grey-100 dark:border-grey-700 my-4" />

          {/* Stats */}
          <div className="space-y-3 py-1">
            <div className="flex justify-between items-center group cursor-pointer">
              <span className="text-xs font-semibold text-grey-500 dark:text-grey-400 group-hover:text-primary-500 transition-colors">Profile viewers</span>
              <span className="text-xs font-bold text-primary-500">{viewedProfile}</span>
            </div>
            <div className="flex justify-between items-center group cursor-pointer">
              <span className="text-xs font-semibold text-grey-500 dark:text-grey-400 group-hover:text-primary-500 transition-colors">Post impressions</span>
              <span className="text-xs font-bold text-primary-500">{impressions}</span>
            </div>
          </div>

          <div className="border-t border-grey-100 dark:border-grey-700 my-4" />

          {/* Location & Year */}
          <div className="space-y-3">
            <div className="flex items-center gap-3 text-grey-600 dark:text-grey-300">
              <MapPin className="w-4 h-4" />
              <span className="text-xs">{location}</span>
            </div>
            <div className="flex items-center gap-3 text-grey-600 dark:text-grey-300">
              <GraduationCap className="w-4 h-4" />
              <span className="text-xs">{Year} Year</span>
            </div>
          </div>

          {isOwnProfile && (
            <div className="mt-4 pt-4 border-t border-grey-100 dark:border-grey-700">
              <button 
                onClick={() => setShowSettings(true)}
                className="w-full flex items-center justify-center gap-2 text-xs font-bold text-grey-500 dark:text-grey-400 hover:bg-grey-50 dark:hover:bg-grey-700 py-2 rounded-md transition-colors"
              >
                <Bell className="w-3.5 h-3.5" />
                Notification Settings
              </button>
            </div>
          )}
        </div>
      </WidgetWrapper>

      <NotificationSettings 
        isOpen={showSettings} 
        onClose={() => setShowSettings(false)} 
      />
    </>
  );
};

export default UserWidget;