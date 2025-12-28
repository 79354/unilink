import React, { useEffect, useRef } from "react";
import Navbar from "scenes/navbar";
import { useSelector } from "react-redux";
import UserWidget from "scenes/widgets/UserWidget";
import MyPostWidget from "scenes/widgets/MyPostWidget";
import PostsWidget from "scenes/widgets/PostsWidget";
import EventsWidget from "scenes/widgets/Events";
import ConnectionListWidget from "scenes/widgets/ConnectionListWidget";
import { motion } from "framer-motion";

const HomePage = () => {
  const { _id, picturePath } = useSelector((state) => state.user);
  const chatbotContainerRef = useRef(null);

  useEffect(() => {
    const script = document.createElement("script");
    script.src = "https://cdn.botpress.cloud/webchat/v1/inject.js";
    script.async = true;
    document.body.appendChild(script);

    script.onload = () => {
      if (chatbotContainerRef.current) {
        const scriptConfig = document.createElement("script");
        scriptConfig.src =
          "https://mediafiles.botpress.cloud/e949b4d4-406a-42bb-978f-d9089eb95921/webchat/config.js";
        scriptConfig.defer = true;
        chatbotContainerRef.current.appendChild(scriptConfig);
      }
    };

    return () => {
      if (document.body.contains(script)) {
        document.body.removeChild(script);
      }
    };
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100 dark:from-slate-900 dark:via-slate-900 dark:to-slate-950 flex flex-col">
      <Navbar />
      
      <div className="max-w-7xl mx-auto w-full px-4 lg:px-[6%] py-6 flex flex-col lg:flex-row gap-6">
        {/* Left Sidebar */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="w-full lg:w-1/4 space-y-4"
        >
          <UserWidget userId={_id} picturePath={picturePath} />
        </motion.div>

        {/* Main Content */}
        <div className="w-full lg:w-1/2 flex flex-col gap-4">
          <MyPostWidget picturePath={picturePath} />
          <PostsWidget userId={_id} />
        </div>

        {/* Right Sidebar */}
        <motion.div 
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className="hidden lg:block w-1/4 space-y-4"
        >
          <EventsWidget />
          <ConnectionListWidget userId={_id} />
        </motion.div>

        {/* Chatbot Container */}
        <div ref={chatbotContainerRef} className="fixed bottom-5 right-5 z-[999]"></div>
      </div>
    </div>
  );
};

export default HomePage;