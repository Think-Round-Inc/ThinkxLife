"use client";

import React from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  TreePine,
  Sun,
  Wind,
  Leaf,
  ArrowRight,
  Users,
  Heart,
  Sparkles,
  Mountain,
} from "lucide-react";
import Image from "next/image";

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

export default function ExteriorSpacesPage() {
  const [currentImageIndex, setCurrentImageIndex] = React.useState(0);

  React.useEffect(() => {
    document.title = 'Exterior Spaces | The Center for The Human Family'
  }, [])

  // Images for slideshow
  const slideshowImages = [
    { src: "/A_Sunset.png", alt: "A Sunset View" },
    { src: "/Amphitheater.png", alt: "Amphitheater" },
    { src: "/Main_Building.png", alt: "Main Building" },
    { src: "/Outside.png", alt: "Outside View" },
    { src: "/Birds_Eye_View.png", alt: "Birds Eye View" },
  ];

  // Auto-advance images
  React.useEffect(() => {
    const interval = setInterval(() => {
      setCurrentImageIndex((prevIndex) => 
        (prevIndex + 1) % slideshowImages.length
      );
    }, 4000); // Change image every 4 seconds

    return () => clearInterval(interval);
  }, [slideshowImages.length]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-blue-50 to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      {/* Hero Section */}
      <section className="relative py-20 overflow-hidden">
        {/* Background Elements */}
        <div className="absolute inset-0">
          <div className="absolute top-20 left-10 w-72 h-72 bg-green-200/30 rounded-full blur-3xl"></div>
          <div className="absolute bottom-20 right-10 w-96 h-96 bg-blue-200/30 rounded-full blur-3xl"></div>
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
              <TreePine className="w-5 h-5 text-green-500 mr-2" />
              <span className="text-gray-700 dark:text-gray-300 font-medium">
                The Center for The Human Family
              </span>
            </motion.div>

            <motion.h1
              variants={fadeInUp}
              className="text-4xl md:text-6xl lg:text-7xl font-bold text-gray-900 dark:text-white mb-6"
            >
              <span className="bg-gradient-to-r from-green-600 via-blue-600 to-purple-600 bg-clip-text text-transparent">
                Exterior Spaces
              </span>
            </motion.h1>

            <motion.p
              variants={fadeInUp}
              className="text-xl md:text-2xl text-gray-600 dark:text-gray-300 mb-12 leading-relaxed max-w-3xl mx-auto"
            >
              Experience the healing power of nature through thoughtfully designed outdoor environments. 
              Our exterior spaces are created to inspire connection, creativity, and collective well-being across 
              generations and communities.
            </motion.p>

            <motion.div
              variants={fadeInUp}
            >
              <Link href="/exterior-spaces/prototype">
                <motion.button
                  whileHover={{
                    scale: 1.05,
                    boxShadow: "0 10px 25px rgba(34, 197, 94, 0.3)"
                  }}
                  whileTap={{ scale: 0.95 }}
                  className="bg-gradient-to-r from-green-500 to-blue-600 hover:from-green-600 hover:to-blue-700 text-white font-semibold py-4 px-8 rounded-full text-lg transition-all duration-300 shadow-lg hover:shadow-green-500/25 flex items-center mx-auto"
                >
                  Enter Space
                  <ArrowRight className="w-5 h-5 ml-2" />
                </motion.button>
              </Link>
            </motion.div>
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
            className="max-w-6xl mx-auto"
          >
            {/* About Section - Updated */}
            <motion.div
              variants={fadeInUp}
              className="bg-white/70 dark:bg-gray-800/70 backdrop-blur-sm rounded-3xl p-8 md:p-12 shadow-xl mb-12"
            >
              <div className="grid md:grid-cols-2 gap-12 items-center">
                <div>
                  <div className="flex items-center mb-6">
                    <div className="w-12 h-12 bg-gradient-to-r from-green-500 to-blue-500 rounded-xl flex items-center justify-center mr-4">
                      <TreePine className="w-6 h-6 text-white" />
                    </div>
                    <h2 className="text-3xl font-bold text-green-600 dark:text-green-400">
                      The Center for Human Family
                    </h2>
                  </div>

                  <div className="space-y-6 text-lg text-gray-700 dark:text-gray-300 leading-relaxed">
                    <p>
                      Welcome to The Center for Human Family, a transformative space dedicated to healing, 
                      connection, and community building. Our thoughtfully designed facility serves as a 
                      sanctuary for individuals and families seeking support, growth, and renewal.
                    </p>
                    <p>
                      Through innovative programs, therapeutic environments, and evidence-based approaches, 
                      we create pathways to healing that honor the human experience while fostering 
                      resilience and hope for future generations.
                    </p>
                  </div>
                </div>
                
                <div className="relative">
                  <div className="aspect-video rounded-2xl shadow-xl overflow-hidden relative">
                    <Image
                      src="/Main_Entrance.png"
                      alt="Main Entrance of The Center for Human Family"
                      fill
                      className="object-cover"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent" />
                  </div>
                </div>
              </div>
            </motion.div>

            {/* Spaces Overview - Updated Title */}
            <motion.div
              variants={fadeInUp}
              className="text-center mb-12"
            >
              <h2 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">
                Inside the Center for Human Family
              </h2>
              <p className="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
                Explore our interconnected healing environments designed to nurture growth and community connection.
              </p>
            </motion.div>

            {/* Features Grid - Updated to 4 cards */}
            <motion.div
              variants={staggerContainer}
              className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-12"
            >
              {[
                { 
                  name: 'Healing Rooms', 
                  icon: Heart, 
                  description: 'Restorative indoor spaces for personal healing',
                  color: 'from-rose-500 to-pink-500',
                  active: false 
                },
                { 
                  name: 'Exterior Spaces', 
                  icon: TreePine, 
                  description: 'Natural outdoor environments for community connection',
                  color: 'from-green-500 to-emerald-500',
                  active: true 
                },
                { 
                  name: 'Air, Water, & Soil', 
                  icon: Wind, 
                  description: 'Essential natural elements for holistic wellness',
                  color: 'from-blue-500 to-cyan-500',
                  active: false 
                },
                { 
                  name: 'Gallery Space', 
                  icon: Sun, 
                  description: 'Creative expression and community art areas',
                  color: 'from-yellow-500 to-orange-500',
                  active: false 
                }
              ].map((space, index) => (
                <motion.div
                  key={space.name}
                  variants={fadeInUp}
                  className={`bg-white/70 dark:bg-gray-800/70 backdrop-blur-sm rounded-2xl p-6 shadow-lg transition-all duration-300 ${
                    space.active 
                      ? 'ring-2 ring-green-300 dark:ring-green-600 shadow-green-500/20' 
                      : 'hover:shadow-xl hover:scale-105'
                  }`}
                >
                  <div className={`w-12 h-12 bg-gradient-to-r ${space.color} rounded-xl flex items-center justify-center mb-4`}>
                    <space.icon className="w-6 h-6 text-white" />
                  </div>
                  <h3 className={`text-xl font-semibold mb-3 ${
                    space.active 
                      ? 'text-green-700 dark:text-green-400' 
                      : 'text-gray-900 dark:text-white'
                  }`}>
                    {space.name}
                  </h3>
                  <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
                    {space.description}
                  </p>
                </motion.div>
              ))}
            </motion.div>

            {/* Immersive Slideshow Images Section */}
            <motion.div
              variants={fadeInUp}
              className="relative mb-12"
            >
              <div className="relative aspect-video bg-gradient-to-br from-green-300 via-blue-200 to-purple-200 rounded-3xl shadow-2xl overflow-hidden">
                {/* Background images with fade transition */}
                <div className="absolute inset-0">
                  {slideshowImages.map((image, index) => (
                    <div
                      key={index}
                      className={`absolute inset-0 transition-opacity duration-1000 ${
                        index === currentImageIndex ? 'opacity-100' : 'opacity-0'
                      }`}
                    >
                      <Image
                        src={image.src}
                        alt={image.alt}
                        fill
                        className="object-cover"
                      />
                    </div>
                  ))}
                </div>
                
                {/* Overlay gradient */}
                <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent" />
                
                {/* Enter Space Button - Centered */}
                <div className="absolute inset-0 flex items-center justify-center">
                  <Link href="/exterior-spaces/prototype">
                    <motion.button 
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      className="bg-white/20 backdrop-blur-sm hover:bg-white/30 text-white px-8 py-4 rounded-full text-lg font-semibold border border-white/30 hover:border-white/50 transition-all duration-300 inline-flex items-center gap-3 shadow-xl"
                    >
                      Enter Space
                      <ArrowRight className="h-5 w-5" />
                    </motion.button>
                  </Link>
                </div>
                
                {/* Bottom text overlay */}
                <div className="absolute bottom-6 left-6 text-white">
                  <h3 className="text-2xl font-bold mb-2">Exterior Spaces Experience</h3>
                  <p className="text-white/90">Immersive outdoor environments for healing and connection</p>
                </div>

                {/* Image indicators/dots */}
                <div className="absolute bottom-6 right-6 flex space-x-2">
                  {slideshowImages.map((_, index) => (
                    <button
                      key={index}
                      onClick={() => setCurrentImageIndex(index)}
                      className={`w-3 h-3 rounded-full transition-all duration-300 ${
                        index === currentImageIndex 
                          ? 'bg-white shadow-lg' 
                          : 'bg-white/50 hover:bg-white/75'
                      }`}
                      aria-label={`Go to image ${index + 1}`}
                    />
                  ))}
                </div>
              </div>
            </motion.div>

            {/* Our Partners */}
            <motion.div
              variants={fadeInUp}
              className="bg-gray-50/70 dark:bg-gray-800/70 backdrop-blur-sm rounded-3xl p-8 md:p-12 shadow-xl text-center mb-12"
            >
              <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">
                Our Partners
              </h2>
              
              <div className="grid md:grid-cols-4 gap-8">
                {[1, 2, 3, 4].map((partner) => (
                  <div
                    key={partner}
                    className="bg-white dark:bg-gray-700 p-8 rounded-2xl shadow-sm hover:shadow-md transition-shadow duration-300"
                  >
                    <div className="h-16 bg-gradient-to-r from-green-200 to-blue-200 rounded-lg flex items-center justify-center">
                      <span className="text-gray-600 dark:text-gray-300 font-semibold">Partner {partner}</span>
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>

            {/* Support Us - Updated with Support.png */}
            <motion.div
              variants={fadeInUp}
              className="bg-white/70 dark:bg-gray-800/70 backdrop-blur-sm rounded-3xl p-8 md:p-12 shadow-xl"
            >
              <div className="grid md:grid-cols-2 gap-12 items-center">
                <div>
                  <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-6">Support Us</h2>
                  <p className="text-lg text-gray-600 dark:text-gray-300 leading-relaxed mb-8">
                    Help us create healing spaces that bring communities together through the power of nature 
                    and thoughtful design. Your support enables us to expand these transformative environments.
                  </p>
                  <div className="flex flex-col sm:flex-row gap-4">
                    <motion.button 
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      className="bg-green-100 hover:bg-green-200 dark:bg-green-900 dark:hover:bg-green-800 text-green-700 dark:text-green-300 px-6 py-3 rounded-full font-semibold transition-all duration-300"
                    >
                      Volunteer
                    </motion.button>
                    <motion.button 
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      className="bg-gradient-to-r from-green-500 to-blue-600 hover:from-green-600 hover:to-blue-700 text-white px-6 py-3 rounded-full font-semibold transition-all duration-300"
                    >
                      Donate
                    </motion.button>
                  </div>
                </div>
                
                <div className="relative">
                  <div className="aspect-square rounded-2xl shadow-xl overflow-hidden relative">
                    <Image
                      src="/Support.png"
                      alt="Community Support"
                      fill
                      className="object-cover"
                    />
                  </div>
                </div>
              </div>
            </motion.div>
          </motion.div>
        </div>
      </section>
    </div>
  );
} 