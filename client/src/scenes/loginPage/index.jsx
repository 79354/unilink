import Form from "./Form";
import { useSelector } from "react-redux";
import { motion } from "framer-motion";
import { Zap, Users, Briefcase } from "lucide-react";

const LoginPage = () => {
  const mode = useSelector((state) => state.mode);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 dark:from-slate-950 dark:via-slate-900 dark:to-indigo-950 font-sans">
      {/* Header */}
      <nav className="w-full bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm px-[10%] py-4 border-b border-slate-200/50 dark:border-slate-700/50">
        <div className="flex items-center justify-between max-w-7xl mx-auto">
          <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
            Uni<span className="text-white bg-gradient-to-r from-blue-600 to-indigo-600 px-2 py-1 rounded-lg ml-1">Link</span>
          </h1>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-[10%] py-16 lg:py-20 flex flex-col lg:flex-row items-center justify-between gap-16">
        <motion.div 
          initial={{ opacity: 0, x: -50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6 }}
          className="w-full lg:w-1/2 space-y-8"
        >
          <div className="space-y-4">
            <h2 className="text-5xl md:text-6xl font-bold text-slate-900 dark:text-white leading-tight">
              Your Professional <br />
              <span className="bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">Network Starts Here</span>
            </h2>
            <p className="text-xl text-slate-600 dark:text-slate-300">
              Connect with students, alumni, and professionals. Share opportunities, build relationships, and grow your network within your university community.
            </p>
          </div>

          {/* Features */}
          <div className="grid gap-4 pt-4">
            {[
              { icon: Zap, title: "Instant Connections", desc: "Network with peers in your university" },
              { icon: Users, title: "Community Driven", desc: "Join meaningful conversations" },
              { icon: Briefcase, title: "Career Growth", desc: "Discover opportunities and mentors" }
            ].map((feature, i) => (
              <motion.div 
                key={i}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.1 }}
                className="flex items-start gap-3"
              >
                <feature.icon className="w-6 h-6 text-blue-600 mt-1 flex-shrink-0" />
                <div>
                  <h3 className="font-semibold text-slate-900 dark:text-white">{feature.title}</h3>
                  <p className="text-sm text-slate-600 dark:text-slate-400">{feature.desc}</p>
                </div>
              </motion.div>
            ))}
          </div>

          {/* Form Card */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-white dark:bg-slate-800 p-8 rounded-2xl shadow-2xl border border-slate-200/50 dark:border-slate-700/50 backdrop-blur-sm w-full max-w-sm"
          >
            <Form />
          </motion.div>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="hidden lg:flex w-1/2 justify-end"
        >
          <div className="relative w-full max-w-md">
            {/* Gradient Blob Background */}
            <div className="absolute inset-0 bg-gradient-to-br from-blue-300 to-indigo-300 dark:from-blue-600/30 dark:to-indigo-600/30 rounded-3xl blur-3xl opacity-40"></div>
            <div className="relative bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-slate-800 dark:to-slate-700 rounded-3xl p-12 border border-blue-200/50 dark:border-slate-600/50 shadow-2xl">
              <div className="space-y-8">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="flex items-center gap-3">
                    <div className="w-12 h-12 bg-gradient-to-br from-blue-400 to-indigo-400 rounded-full"></div>
                    <div className="space-y-1">
                      <div className="h-2 bg-slate-300 dark:bg-slate-600 rounded w-20"></div>
                      <div className="h-2 bg-slate-200 dark:bg-slate-700 rounded w-16"></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default LoginPage;