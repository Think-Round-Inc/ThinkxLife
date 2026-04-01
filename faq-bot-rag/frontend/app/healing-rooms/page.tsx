"use client";

import React from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  Heart,
  Users,
  Shield,
  MessageCircle,
  ArrowRight,
  Sparkles,
  Eye,
  Brain,
} from "lucide-react";

// Animation variants
const fadeInUp = {
  hidden: { opacity: 0, y: 60 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.6 },
  },
};

const staggerContainer = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.3,
    },
  },
};

export default function HealingRoomsPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-rose-50 via-pink-50 to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      {/* Hero Section */}
      <section className="relative py-20 overflow-hidden">
        {/* Background Elements */}
        <div className="absolute inset-0">
          <div className="absolute top-20 left-10 w-72 h-72 bg-rose-200/30 rounded-full blur-3xl"></div>
          <div className="absolute bottom-20 right-10 w-96 h-96 bg-purple-200/30 rounded-full blur-3xl"></div>
        </div>

        <div className="container mx-auto px-6 relative z-10">
          <motion.div
            initial="hidden"
            animate="visible"
            variants={staggerContainer}
            className="text-center max-w-4xl mx-auto"
          >
            <motion.div
              variants={fadeInUp}
              className="inline-flex items-center bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-full px-6 py-3 mb-8 shadow-lg"
            >
              <Heart className="w-5 h-5 text-rose-500 mr-2" />
              <span className="text-gray-700 dark:text-gray-300 font-medium">
                Virtual - Second Floor
              </span>
            </motion.div>

            <motion.h1
              variants={fadeInUp}
              className="text-4xl md:text-6xl lg:text-7xl font-bold text-gray-900 dark:text-white mb-6"
            >
              <span className="bg-gradient-to-r from-rose-600 via-pink-600 to-purple-600 bg-clip-text text-transparent">
                Healing Rooms
              </span>
            </motion.h1>

            <motion.p
              variants={fadeInUp}
              className="text-xl md:text-2xl text-gray-600 dark:text-gray-300 mb-12 leading-relaxed max-w-3xl mx-auto"
            >
              We are deeply dedicated to supporting your journey of healing and empowerment,
              helping you overcome and prevent the lasting effects of childhood trauma.
            </motion.p>
          </motion.div>
        </div>
      </section>

      {/* Main Content */}
      <section className="py-16">
        <div className="container mx-auto px-6">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={staggerContainer}
            className="max-w-4xl mx-auto"
          >
            {/* About Section */}
            <motion.div
              variants={fadeInUp}
              className="bg-white/70 dark:bg-gray-800/70 backdrop-blur-sm rounded-3xl p-8 md:p-12 shadow-xl mb-12"
            >
              <div className="flex items-center mb-6">
                <div className="w-12 h-12 bg-gradient-to-r from-rose-500 to-pink-500 rounded-xl flex items-center justify-center mr-4">
                  <Users className="w-6 h-6 text-white" />
                </div>
                <h2 className="text-3xl font-bold text-gray-900 dark:text-white">
                  About Healing Rooms
                </h2>
              </div>

              <div className="space-y-6 text-lg text-gray-700 dark:text-gray-300 leading-relaxed">
                <p>
                  Healing Rooms offer programs for individuals and families to recognize and heal
                  from trauma through compassionate care and personalized support.
                </p>
                <p>
                  The Healing Rooms are located on the second floor of the Virtual and
                  provide recovery spaces specifically focused on healing and preventing childhood trauma.
                </p>
              </div>
            </motion.div>

            {/* Features Grid */}
            <motion.div
              variants={staggerContainer}
              className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12"
            >
              <motion.div
                variants={fadeInUp}
                className="bg-white/70 dark:bg-gray-800/70 backdrop-blur-sm rounded-2xl p-6 shadow-lg"
              >
                <div className="w-10 h-10 bg-gradient-to-r from-red-500 to-orange-500 rounded-lg flex items-center justify-center mb-4">
                  <Shield className="w-5 h-5 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3">
                  ACEs Assessment
                </h3>
                <p className="text-gray-600 dark:text-gray-300">
                  Understanding Adverse Childhood Experiences and their impact on your healing journey through comprehensive assessment and awareness.
                </p>
              </motion.div>

              <motion.div
                variants={fadeInUp}
                className="bg-white/70 dark:bg-gray-800/70 backdrop-blur-sm rounded-2xl p-6 shadow-lg"
              >
                <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-lg flex items-center justify-center mb-4">
                  <Eye className="w-5 h-5 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3">
                  Vision with Zoe
                </h3>
                <p className="text-gray-600 dark:text-gray-300">
                  Collaborative visioning sessions with Zoe to help you see possibilities for healing and create a clear path forward.
                </p>
              </motion.div>

              <motion.div
                variants={fadeInUp}
                className="bg-white/70 dark:bg-gray-800/70 backdrop-blur-sm rounded-2xl p-6 shadow-lg"
              >
                <div className="w-10 h-10 bg-gradient-to-r from-pink-500 to-rose-500 rounded-lg flex items-center justify-center mb-4">
                  <Heart className="w-5 h-5 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3">
                  Empathy-Centered Care
                </h3>
                <p className="text-gray-600 dark:text-gray-300">
                  Deep empathetic understanding and validation of your experiences, creating a safe space for authentic healing.
                </p>
              </motion.div>

              <motion.div
                variants={fadeInUp}
                className="bg-white/70 dark:bg-gray-800/70 backdrop-blur-sm rounded-2xl p-6 shadow-lg"
              >
                <div className="w-10 h-10 bg-gradient-to-r from-green-500 to-emerald-500 rounded-lg flex items-center justify-center mb-4">
                  <MessageCircle className="w-5 h-5 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3">
                  Therapeutic Chat
                </h3>
                <p className="text-gray-600 dark:text-gray-300">
                  Ongoing supportive conversations designed to process experiences and build resilience through guided dialogue.
                </p>
              </motion.div>
            </motion.div>

            {/* Zoe AI Assistant Section */}
            <motion.div
              variants={fadeInUp}
              className="bg-white rounded-3xl p-8 md:p-12 shadow-xl text-center"
            >
              <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-2xl mb-6">
                <MessageCircle className="w-8 h-8 text-white" />
              </div>

              <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
                Meet Zoe - Your AI Healing Companion
              </h2>

              <p className="text-lg text-gray-600 dark:text-gray-300 mb-8 max-w-2xl mx-auto leading-relaxed">
                Zoe is our compassionate AI assistant, specially designed to provide supportive guidance
                and resources for your healing journey. She offers 24/7 availability with trauma-informed
                responses.
              </p>

              <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
                <Link href="/healing-rooms/chat">
                  <motion.button
                    whileHover={{
                      scale: 1.05,
                      boxShadow: "0 10px 25px rgba(59, 130, 246, 0.3)"
                    }}
                    whileTap={{ scale: 0.95 }}
                    className="bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 text-white font-semibold py-4 px-8 rounded-full text-lg transition-all duration-300 shadow-lg hover:shadow-blue-500/25 flex items-center"
                  >
                    Try Zoe Now
                    <ArrowRight className="w-5 h-5 ml-2" />
                  </motion.button>
                </Link>

                <div className="text-sm text-gray-500 dark:text-gray-400">
                  Free • Confidential • Available 24/7
                </div>
              </div>
            </motion.div>

            {/* Access Virtual Healing Rooms Button */}
            <motion.div
              variants={fadeInUp}
              className="text-center mt-12"
            >
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="bg-gray-400 cursor-not-allowed text-white font-semibold py-4 px-8 rounded-full text-lg transition-all duration-300 shadow-lg"
                disabled
              >
                Access Virtual Healing Rooms<sup className="text-xs ml-1 text-[#5B2655]">Coming Soon</sup>
              </motion.button>
              <p className="text-gray-500 dark:text-gray-400 mt-3 text-sm">
                Full virtual healing environment launching soon
              </p>
            </motion.div>
          </motion.div>
        </div>
      </section>
    </div>
  );
}
