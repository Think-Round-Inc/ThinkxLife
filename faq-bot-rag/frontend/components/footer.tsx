'use client';

import { useState } from 'react';
import Link from "next/link";
import {
  Facebook,
  Twitter,
  Instagram,
  Mail,
  Phone,
  MapPin,
  Heart,
} from "lucide-react";

export default function Footer() {
  const [_hoveredSocial, setHoveredSocial] = useState<string | null>(null);

  const socialLinks = [
    { icon: Facebook, name: 'facebook', href: '#', color: 'hover:text-blue-600' },
    { icon: Twitter, name: 'twitter', href: '#', color: 'hover:text-sky-500' },
    { icon: Instagram, name: 'instagram', href: '#', color: 'hover:text-pink-600' },
  ];

  return (
    <footer className="bg-white border-t border-gray-200/60">
      {/* Main Footer Content - Compact */}
      <div className="max-w-7xl mx-auto px-6 md:px-12 lg:px-24 py-3">
        <div className="flex flex-col md:flex-row justify-between items-center gap-3">
          
          {/* Brand & Contact Info - Left */}
          <div className="flex flex-col md:flex-row items-center gap-3">
            {/* Brand - Match Header Logo */}
            <div className="text-center md:text-left">
              <Link href="/" className="inline-block">
                <span className="text-lg font-bold tracking-wider text-black">
                  ThinkLife
                  <sup className="text-xs font-normal text-gray-700 ml-2 tracking-normal flex items-center">
                    from <img src="/tr_logo.png" alt="Think Round" className="w-3 h-3 ml-1" /> Think Round, Inc
                  </sup>
                </span>
              </Link>
            </div>

            {/* Contact Info - Compact */}
            <div className="flex flex-wrap items-center gap-2 text-xs text-gray-500">
              <div className="flex items-center gap-1">
                <MapPin className="w-3 h-3 text-black" />
                <span>San Francisco, CA</span>
              </div>
              <div className="flex items-center gap-1">
                <Phone className="w-3 h-3 text-black" />
                <span>(415) 602-9599</span>
              </div>
              <div className="flex items-center gap-1">
                <Mail className="w-3 h-3 text-black" />
                <span>info@thinkround.org</span>
              </div>
            </div>
          </div>

          {/* Social Links & Support - Right */}
          <div className="flex items-center gap-3">
            {/* Social Links */}
            <div className="flex gap-1">
              {socialLinks.map((social) => (
                <Link
                  key={social.name}
                  href={social.href}
                  className={`p-1.5 rounded-md bg-gray-50 hover:bg-gray-100 ${social.color} transition-all duration-300 hover:scale-110`}
                  onMouseEnter={() => setHoveredSocial(social.name)}
                  onMouseLeave={() => setHoveredSocial(null)}
                >
                  <social.icon className="w-3 h-3" />
                </Link>
              ))}
            </div>

            {/* Support Button - Compact */}
            <Link 
              href="https://www.thinkround.org/donate" 
              target="_blank" 
              rel="noopener noreferrer"
            >
              <div className="inline-flex items-center gap-1.5 bg-black hover:bg-gray-800 text-white px-3 py-1.5 rounded-full text-xs font-medium shadow-sm hover:shadow-black/25 transition-all duration-300 transform hover:scale-105">
                <Heart className="w-3 h-3" />
                Support
              </div>
            </Link>
          </div>
        </div>
      </div>

      {/* Bottom Copyright - Very Compact */}
      <div className="border-t border-gray-100 py-2">
        <div className="max-w-7xl mx-auto px-6 md:px-12 lg:px-24">
          <div className="flex flex-col md:flex-row justify-between items-center gap-1 text-xs text-gray-400">
            <div className="flex items-center gap-2">
              <span>&copy; {new Date().getFullYear()} Think Round, Inc.</span>
              <span>•</span>
              <span className="flex items-center gap-1">
                Made with <Heart className="w-2.5 h-2.5 text-red-500" /> for humanity
              </span>
            </div>
            
            <div className="flex items-center gap-2">
              <Link href="/privacy" className="hover:text-black transition-colors">
                Privacy
              </Link>
              <span>•</span>
              <Link href="/terms" className="hover:text-black transition-colors">
                Terms
              </Link>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
