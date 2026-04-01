"use client";

import React, { useRef } from "react";
import Link from "next/link";
import {
  motion,
  useScroll,
  useTransform,
} from "framer-motion";
import {
  Shield,
  BookOpen,
  Brain,
  Users,
  Target,
  Heart,
  Palette,
  GraduationCap,
  Globe,
  MessageCircle,
  Sparkles,
  Code,
} from "lucide-react";

// Animation variants
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

const fadeInUp = {
  hidden: { opacity: 0, y: 60 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.6 },
  },
};

// Define interfaces
interface FeatureContent {
  title: string;
  icon: React.ReactNode;
  tagline: string;
  bullets: {
    title: string;
    description: string;
  }[];
  cta: {
    label: string;
    destination: string;
  };
}

export default function AIAwarenessPage() {
  const { scrollY } = useScroll();
  const progressBarWidth = useTransform(scrollY, [0, 2000], ["0%", "100%"]);
  const philosophySectionRef = useRef<HTMLElement>(null);

  const scrollToPhilosophy = () => {
    philosophySectionRef.current?.scrollIntoView({
      behavior: 'smooth',
      block: 'start'
    });
  };

  const features: FeatureContent[] = [
    {
      icon: <Heart className="w-6 h-6" />,
      title: "Trauma-Informed AI",
      tagline:
        "Our AI systems are designed with trauma-informed care principles, ensuring safe and supportive interactions for all users.",
      bullets: [
        {
          title: "Zoe AI Companion",
          description:
            "Our empathetic AI companion Zoe provides 24/7 support with trauma-informed responses and emotional intelligence.",
        },
        {
          title: "ACEs Integration",
          description:
            "Adverse Childhood Experiences (ACEs) assessment integration helps personalize interactions for healing journeys.",
        },
        {
          title: "Crisis Detection",
          description:
            "Advanced algorithms detect crisis situations and provide appropriate resources and professional referrals.",
        },
        {
          title: "Safety First",
          description:
            "Every AI interaction is filtered through our trauma-safety protocols to prevent re-traumatization.",
        },
      ],
      cta: {
        label: "Experience Zoe →",
        destination: "/chat",
      },
    },
    {
      icon: <Palette className="w-6 h-6" />,
      title: "AI in Arts Programs",
      tagline:
        "Integrating AI into our arts programs while preserving human creativity and cultural authenticity.",
      bullets: [
        {
          title: "Creative Collaboration",
          description:
            "AI tools that enhance human creativity rather than replace artists, supporting our community art programs.",
        },
        {
          title: "Cultural Preservation",
          description:
            "Using AI to document and preserve cultural narratives from diverse communities in San Francisco's Bayview-Hunters Point.",
        },
        {
          title: "Program Accessibility",
          description:
            "AI-powered personalized learning that adapts to different learning styles and cultural backgrounds.",
        },
        {
          title: "Youth Empowerment",
          description:
            "Ensuring AI enhancements in our programs are accessible to all community members regardless of technological background.",
        },
      ],
      cta: {
        label: "Explore Programs →",
        destination: "https://www.thinkround.org/art",
      },
    },
    {
      icon: <Globe className="w-6 h-6" />,
      title: "Community & Global Impact",
      tagline:
        "Leveraging AI to strengthen communities and create positive global change through our Center for the Human Family vision.",
      bullets: [
        {
          title: "Community Building",
          description:
            "AI-powered tools that connect community members, facilitate cultural exchange, and strengthen social bonds.",
        },
        {
          title: "Social Justice",
          description:
            "Using AI to identify and address systemic inequalities while ensuring algorithmic fairness in our programs.",
        },
        {
          title: "Global Connection",
          description:
            "Creating AI-mediated connections between communities worldwide, fostering understanding and collaboration.",
        },
        {
          title: "Environmental Awareness",
          description:
            "AI systems that promote environmental consciousness and sustainable practices in our community work.",
        },
      ],
      cta: {
        label: "Join Our Community →",
        destination: "https://www.thinkround.org/aboutus",
      },
    },
  ];

  const steps = [
    {
      number: "01",
      title: "Enhance, Don't Replace",
      description: "AI amplifies our artists, healers, and educators rather than replacing human creativity and care",
    },
    {
      number: "02",
      title: "Trauma-Informed AI",
      description: "Our AI tools in healing rooms are designed with trauma-informed care principles at their core",
    },
    {
      number: "03",
      title: "Cultural Preservation",
      description: "AI helps document, preserve, and celebrate cultural traditions within our community programs",
    },
    {
      number: "04",
      title: "Creative Collaboration",
      description: "Artists and AI work together in our studios to create innovative expressions while maintaining authenticity",
    },
  ];

  const programs = [
    {
      icon: <Heart className="w-8 h-8" />,
      title: "Healing Rooms Enhancement",
      description: "AI companions like Zoe provide trauma-informed support and personalized healing experiences",
    },
    {
      icon: <Palette className="w-8 h-8" />,
      title: "Arts Program Integration",
      description: "AI tools help artists explore new creative possibilities while preserving authentic expression",
    },
    {
      icon: <Globe className="w-8 h-8" />,
      title: "Paradise Project Support",
      description: "AI assists in community building, cultural preservation, and environmental stewardship initiatives",
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-indigo-50 to-blue-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      {/* Progress Bar */}
      <motion.div
        className="fixed top-0 right-0 h-1 bg-gradient-to-r from-purple-500 to-indigo-600 z-50"
        style={{ width: progressBarWidth }}
      />

      {/* Hero Section */}
      <section className="relative py-20 overflow-hidden">
        {/* Background Elements */}
        <div className="absolute inset-0">
          <div className="absolute top-20 left-10 w-72 h-72 bg-purple-200/30 rounded-full blur-3xl"></div>
          <div className="absolute bottom-20 right-10 w-96 h-96 bg-indigo-200/30 rounded-full blur-3xl"></div>
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
              <Brain className="w-5 h-5 text-purple-500 mr-2" />
              <span className="text-gray-700 dark:text-gray-300 font-medium">
                Think Round Inc • AI for Humanity
              </span>
            </motion.div>

            <motion.h1
              variants={fadeInUp}
              className="text-4xl md:text-6xl lg:text-7xl font-bold text-gray-900 dark:text-white mb-6"
            >
              AI that serves{" "}
              <span className="bg-gradient-to-r from-purple-600 via-indigo-600 to-blue-600 bg-clip-text text-transparent">
                humanity
              </span>
            </motion.h1>
            <motion.p
              variants={fadeInUp}
              className="text-xl md:text-2xl text-gray-600 dark:text-gray-300 mb-12 leading-relaxed max-w-3xl mx-auto"
            >
              Discover how Think Round Inc uses artificial intelligence to enhance our arts programs, 
              healing rooms, paradise project, and community initiatives while preserving our core values 
              of human dignity, cultural authenticity, and trauma-informed care.
            </motion.p>

            <motion.div
              variants={fadeInUp}
              className="flex flex-col sm:flex-row gap-4 justify-center items-center"
            >
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={scrollToPhilosophy}
                className="bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white font-semibold py-4 px-8 rounded-full text-lg transition-all duration-300 shadow-lg hover:shadow-purple-500/25"
              >
                Explore Our AI Applications
              </motion.button>
              <Link href="/chat">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="bg-white hover:bg-gray-100 text-purple-600 font-semibold py-4 px-8 rounded-full text-lg transition-all duration-300 shadow-lg border border-purple-200 hover:border-purple-300"
                >
                  Chat with Zoe
                </motion.button>
              </Link>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Philosophy Section */}
      <section id="philosophy" ref={philosophySectionRef} className="py-20">
        <div className="container mx-auto px-6">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={staggerContainer}
            className="text-center mb-16"
          >
            <motion.h2
              variants={fadeInUp}
              className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4"
            >
              How We Use AI
            </motion.h2>
            <motion.p
              variants={fadeInUp}
              className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto"
            >
              At Think Round Inc, we believe "Earth is home. Humans are family. AI for humanity." 
              Our approach to artificial intelligence is rooted in human dignity, cultural respect, and healing.
            </motion.p>
          </motion.div>

          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={staggerContainer}
            className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto"
          >
            {features.map((feature, index) => (
              <motion.div
                key={index}
                variants={fadeInUp}
                whileHover={{
                  y: -10,
                  boxShadow: "0 20px 40px rgba(0,0,0,0.1)",
                }}
                className="bg-white/70 dark:bg-gray-800/70 backdrop-blur-sm rounded-2xl shadow-lg p-8 border border-gray-100 dark:border-gray-700 group"
              >
                <motion.div
                  whileHover={{ scale: 1.1, rotate: 5 }}
                  className="text-purple-600 dark:text-purple-400 mb-6 inline-block p-3 bg-purple-100 dark:bg-purple-900/20 rounded-xl"
                >
                  {feature.icon}
                </motion.div>
                <h3 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4 group-hover:text-purple-600 transition-colors">
                  {feature.title}
                </h3>
                <p className="text-gray-600 dark:text-gray-300 mb-6 leading-relaxed">
                  {feature.tagline}
                </p>
                <div className="space-y-3 mb-6">
                  {feature.bullets.map((bullet, bulletIndex) => (
                    <div
                      key={bulletIndex}
                      className="flex items-start space-x-3"
                    >
                      <div className="w-2 h-2 bg-purple-600 rounded-full mt-2 flex-shrink-0" />
                      <div>
                        <span className="font-medium text-gray-900 dark:text-white">
                          {bullet.title}
                        </span>
                        <span className="text-gray-600 dark:text-gray-300">
                          {" "}
                          — {bullet.description}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
                <Link href={feature.cta.destination}>
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="w-full bg-gradient-to-r from-purple-500 to-indigo-600 hover:from-purple-600 hover:to-indigo-700 text-white font-semibold py-3 px-6 rounded-xl transition-all duration-300 group-hover:shadow-lg shadow-lg hover:shadow-purple-500/25"
                  >
                    {feature.cta.label}
                  </motion.button>
                </Link>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* How We Work Section */}
      <section
        id="applications"
        className="py-20 bg-white/50 dark:bg-gray-800/50 backdrop-blur-sm"
      >
        <div className="container mx-auto px-6">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={staggerContainer}
            className="text-center mb-16"
          >
            <motion.h2
              variants={fadeInUp}
              className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4"
            >
              How We Integrate AI
            </motion.h2>
            <motion.p
              variants={fadeInUp}
              className="text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto"
            >
              Our four-step approach ensures AI enhances rather than replaces human connection and creativity
            </motion.p>
          </motion.div>

          <div className="max-w-4xl mx-auto">
            {steps.map((step, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: index % 2 === 0 ? -50 : 50 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: index * 0.2 }}
                className={`flex items-center mb-12 ${
                  index % 2 === 1 ? "flex-row-reverse" : ""
                }`}
              >
                <div className="flex-1">
                  <div
                    className={`${
                      index % 2 === 0 ? "text-right pr-8" : "text-left pl-8"
                    }`}
                  >
                    <motion.div
                      whileHover={{ scale: 1.1 }}
                      className="text-6xl font-bold text-purple-200 dark:text-purple-800 mb-2"
                    >
                      {step.number}
                    </motion.div>
                    <h3 className="text-2xl font-semibold text-gray-900 dark:text-white mb-2">
                      {step.title}
                    </h3>
                    <p className="text-gray-600 dark:text-gray-300">
                      {step.description}
                    </p>
                  </div>
                </div>
                <motion.div
                  whileHover={{ scale: 1.2, rotate: 10 }}
                  className="w-16 h-16 bg-gradient-to-r from-purple-500 to-indigo-600 rounded-full flex items-center justify-center text-white font-bold text-xl mx-8 flex-shrink-0 shadow-lg"
                >
                  {index + 1}
                </motion.div>
                <div className="flex-1" />
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Programs Section */}
      <section id="programs" className="py-20 bg-white/50 dark:bg-gray-800/50 backdrop-blur-sm">
        <div className="container mx-auto px-6">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={staggerContainer}
            className="text-center mb-16"
          >
            <motion.h2
              variants={fadeInUp}
              className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4"
            >
              Our AI Programs
            </motion.h2>
            <motion.p
              variants={fadeInUp}
              className="text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto"
            >
              See how AI enhances our healing rooms, arts programs, paradise project, and community initiatives
            </motion.p>
          </motion.div>

          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={staggerContainer}
            className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto"
          >
            {programs.map((program, index) => (
              <motion.div
                key={index}
                variants={fadeInUp}
                whileHover={{
                  y: -5,
                  boxShadow: "0 10px 25px rgba(0,0,0,0.1)",
                }}
                className="bg-white/70 dark:bg-gray-800/70 backdrop-blur-sm rounded-xl p-6 shadow-lg text-center"
              >
                <motion.div
                  whileHover={{ scale: 1.1, rotate: 5 }}
                  className="text-purple-600 dark:text-purple-400 mb-4 inline-block"
                >
                  {program.icon}
                </motion.div>
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                  {program.title}
                </h3>
                <p className="text-gray-600 dark:text-gray-300 mb-4">
                  {program.description}
                </p>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="text-purple-600 dark:text-purple-400 hover:text-purple-700 dark:hover:text-purple-300 font-semibold transition-colors"
                >
                  Learn More →
                </motion.button>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>
    </div>
  );
}
