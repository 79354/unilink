import Form from "./Form";
import { useSelector } from "react-redux";
import { motion } from "framer-motion";

const LoginPage = () => {
  const mode = useSelector((state) => state.mode);

  return (
    <div className="min-h-screen bg-grey-50 dark:bg-grey-900 font-sans">
      {/* Header */}
      <nav className="w-full bg-white dark:bg-grey-800 px-[10%] py-4 shadow-sm border-b border-grey-200 dark:border-grey-700">
        <div className="flex items-center justify-between max-w-7xl mx-auto">
          <h1 className="text-2xl font-bold text-primary-500">
            Uni<span className="bg-primary-500 text-white px-1.5 py-0.5 rounded-sm ml-0.5">Link</span>
          </h1>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-[10%] py-12 flex flex-col lg:flex-row items-center justify-between gap-12">
        <motion.div 
          initial={{ opacity: 0, x: -50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6 }}
          className="w-full lg:w-1/2"
        >
          <h2 className="text-4xl md:text-5xl font-light text-primary-600 dark:text-primary-400 mb-8 leading-tight">
            Welcome to your <br />
            <span className="font-bold">professional university community</span>
          </h2>
          
          <div className="bg-white dark:bg-grey-800 p-8 rounded-xl linkedin-card w-full max-w-lg">
            <Form />
          </div>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, x: 50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="hidden lg:block w-1/2"
        >
          <img 
            src="https://static.licdn.com/aero-v1/sc/h/d58zfe6h3yc07zccu8dh9v97t" 
            alt="Hero" 
            className="w-full h-auto object-contain"
          />
        </motion.div>
      </div>
    </div>
  );
};

export default LoginPage;