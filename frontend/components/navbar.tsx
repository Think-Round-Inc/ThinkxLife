"use client";

import { useState, useEffect, useCallback } from "react";
import { usePathname } from "next/navigation";
import Link from "next/link";
import { Menu, X, Heart, User, LogOut } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useAuth } from "@/hooks/useAuth";

export default function Navbar() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);
  const { isAuthenticated, isLoading, user, login, logout } = useAuth();
  const pathname = usePathname();

  // Check if user is actively using features
  const isUsingAIAwareness = pathname?.startsWith('/inside-our-ai');
  const isUsingHealingRooms = pathname?.startsWith('/healing-rooms');
  const isUsingExteriorSpaces = pathname?.startsWith('/exterior-spaces');

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Get first letter of first name
  const getFirstLetter = (name: string | null | undefined, email?: string | null) => {
    if (name) {
      const firstName = name.split(" ")[0];
      return firstName[0].toUpperCase();
    }
    if (email) {
      return email[0].toUpperCase();
    }
    return "U";
  };

  // Generate luxury color based on first letter (consistent color per user)
  const getLuxuryColor = (letter: string) => {
    const luxuryColors = [
      { bg: "bg-gradient-to-br from-amber-500 to-amber-700", text: "text-white" },
      { bg: "bg-gradient-to-br from-emerald-500 to-emerald-700", text: "text-white" },
      { bg: "bg-gradient-to-br from-rose-500 to-rose-700", text: "text-white" },
      { bg: "bg-gradient-to-br from-indigo-500 to-indigo-700", text: "text-white" },
      { bg: "bg-gradient-to-br from-purple-500 to-purple-700", text: "text-white" },
      { bg: "bg-gradient-to-br from-teal-500 to-teal-700", text: "text-white" },
      { bg: "bg-gradient-to-br from-pink-500 to-pink-700", text: "text-white" },
      { bg: "bg-gradient-to-br from-blue-500 to-blue-700", text: "text-white" },
      { bg: "bg-gradient-to-br from-violet-500 to-violet-700", text: "text-white" },
      { bg: "bg-gradient-to-br from-cyan-500 to-cyan-700", text: "text-white" },
    ];
    
    // Use letter to consistently assign color
    const index = letter.charCodeAt(0) % luxuryColors.length;
    return luxuryColors[index];
  };

  const handleLogout = () => {
    logout(window.location.origin);
  };

  // Memoized login handler to prevent re-render issues
  const handleLogin = useCallback(async (e?: React.MouseEvent) => {
    if (e) {
      e.preventDefault();
      e.stopPropagation();
    }
    // Trigger login immediately (now async)
    await login(window.location.origin);
  }, [login]);

  return (
    <header className="fixed top-0 left-0 right-0 z-50 transition-all duration-300">
      {/* Clean White Navigation Bar */}
      <nav className={`py-2 px-6 md:px-12 lg:px-24 transition-all duration-300 ${
        isScrolled
          ? 'bg-white/95 backdrop-blur-xl border-b border-gray-200/60 shadow-sm'
          : 'bg-white/90 backdrop-blur-md border-b border-gray-100/40'
      }`}>
        <div className="flex items-center justify-between">
          {/* Logo - Left */}
          <Link href="/" className="flex items-center group">
            <span className="text-xl font-bold tracking-wider text-black">
              ThinkLife
              <sup className="text-xs font-normal text-gray-700 ml-2 tracking-normal flex items-center">
                from <img src="/tr_logo.png" alt="Think Round" className="w-3 h-3 ml-1" /> Think Round, Inc
              </sup>
            </span>
          </Link>

          {/* Desktop Navigation - Center */}
          <div className="hidden md:flex items-center space-x-6">
            <Link 
              href="/inside-our-ai" 
              className={`relative text-gray-600 hover:text-black text-sm font-medium transition-colors duration-300 py-2 group ${
                isUsingAIAwareness ? 'text-black' : ''
              }`}
            >
              Inside our AI
              <div className={`absolute bottom-0 left-0 h-0.5 bg-black transition-all duration-300 ${
                isUsingAIAwareness ? 'w-full' : 'w-0 group-hover:w-full'
              }`}></div>
            </Link>
            <Link 
              href="/healing-rooms" 
              className={`relative text-gray-600 hover:text-black text-sm font-medium transition-colors duration-300 py-2 group ${
                isUsingHealingRooms ? 'text-black' : ''
              }`}
            >
              Healing Rooms
              <div className={`absolute bottom-0 left-0 h-0.5 bg-black transition-all duration-300 ${
                isUsingHealingRooms ? 'w-full' : 'w-0 group-hover:w-full'
              }`}></div>
            </Link>
            <Link 
              href="/exterior-spaces" 
              className={`relative text-gray-600 hover:text-black text-sm font-medium transition-colors duration-300 py-2 group ${
                isUsingExteriorSpaces ? 'text-black' : ''
              }`}
            >
              Exterior Spaces
              <div className={`absolute bottom-0 left-0 h-0.5 bg-black transition-all duration-300 ${
                isUsingExteriorSpaces ? 'w-full' : 'w-0 group-hover:w-full'
              }`}></div>
            </Link>
            <Link
              href="https://www.thinkround.org/aboutus"
              target="_blank"
              rel="noopener noreferrer"
              className="relative text-gray-600 hover:text-black font-medium transition-colors duration-300 text-sm py-2 group"
            >
              About
              <div className="absolute bottom-0 left-0 w-0 h-0.5 bg-black transition-all duration-300 group-hover:w-full"></div>
            </Link>
            <Link
              href="https://thinkround.shop/"
              target="_blank"
              rel="noopener noreferrer"
              className="relative text-gray-600 hover:text-black font-medium transition-colors duration-300 text-sm py-2 group"
            >
              Shop
              <div className="absolute bottom-0 left-0 w-0 h-0.5 bg-black transition-all duration-300 group-hover:w-full"></div>
            </Link>
            <Link
              href="https://www.thinkround.org/donate"
              target="_blank"
              rel="noopener noreferrer"
              className="relative text-gray-600 hover:text-black font-medium transition-colors duration-300 text-sm py-2 group"
            >
              Donate
              <div className="absolute bottom-0 left-0 w-0 h-0.5 bg-black transition-all duration-300 group-hover:w-full"></div>
            </Link>
          </div>

          {/* Authentication Section - Right */}
          <div className="flex items-center space-x-3">
            {isAuthenticated && user ? (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <button className="flex items-center space-x-2 hover:bg-gray-50 rounded-lg p-2 transition-all duration-300 group">
                    {/* Profile Avatar with First Letter */}
                    <div className="relative">
                      <div className="w-9 h-9 rounded-lg border-2 border-gray-300 shadow-sm group-hover:border-gray-400 transition-all duration-300 overflow-hidden">
                        {(() => {
                          const firstLetter = getFirstLetter(user.firstName || user.name, user.email);
                          const colorScheme = getLuxuryColor(firstLetter);
                          return (
                            <div className={`w-full h-full ${colorScheme.bg} flex items-center justify-center ${colorScheme.text} font-bold text-sm`}>
                              {firstLetter}
                            </div>
                          );
                        })()}
                      </div>
                      {/* Online indicator */}
                      <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-green-500 border-2 border-white rounded-full"></div>
                    </div>
                    <div className="hidden md:block text-left">
                      <div className="text-sm font-medium text-gray-800">
                        {user.firstName || user.name?.split(' ')[0] || user.email?.split('@')[0] || 'User'}
                      </div>
                    </div>
                  </button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-52 bg-white/95 backdrop-blur-sm border-gray-200 shadow-lg">
                  <div className="px-3 py-2">
                    <p className="text-sm font-medium text-gray-800">
                      {user.name || user.email}
                    </p>
                    {user.email && (
                      <p className="text-xs text-gray-500">
                        {user.email}
                      </p>
                    )}
                  </div>
                  <DropdownMenuSeparator className="bg-gray-200" />
                  <DropdownMenuItem asChild>
                    <Link href="/chat" className="flex items-center w-full px-3 py-2 text-sm hover:bg-gray-50">
                      <User className="w-4 h-4 mr-2" />
                      Chat
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuSeparator className="bg-gray-200" />
                  <DropdownMenuItem
                    onClick={handleLogout}
                    className="flex items-center w-full px-3 py-2 text-sm text-red-600 hover:bg-red-50"
                  >
                    <LogOut className="w-4 h-4 mr-2" />
                    Sign Out
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            ) : (
              <Button 
                className="bg-black hover:bg-gray-800 text-white px-6 py-2 rounded-full text-sm font-medium shadow-lg hover:shadow-black/25 transition-all duration-300 transform hover:scale-105"
                onClick={handleLogin}
              >
                Get Started
              </Button>
            )}

            {/* Mobile Menu Button */}
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="md:hidden p-2 rounded-lg hover:bg-gray-50 transition-colors duration-300"
            >
              {isMenuOpen ? (
                <X className="w-5 h-5 text-gray-600" />
              ) : (
                <Menu className="w-5 h-5 text-gray-600" />
              )}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {isMenuOpen && (
          <div className="md:hidden mt-3 py-3 bg-white/90 backdrop-blur-sm rounded-lg border border-gray-100 shadow-lg">
            <div className="flex flex-col space-y-2 px-4">
              <Link
                href="/inside-our-ai"
                className={`py-2 transition-colors duration-300 flex items-center ${
                  isUsingAIAwareness ? 'text-black font-medium' : 'text-gray-600 hover:text-black'
                }`}
                onClick={() => setIsMenuOpen(false)}
              >
                Inside our AI
                {isUsingAIAwareness && (
                  <div className="ml-2 w-1 h-4 bg-black rounded-full"></div>
                )}
              </Link>
              <Link
                href="/healing-rooms"
                className={`py-2 transition-colors duration-300 flex items-center ${
                  isUsingHealingRooms ? 'text-black font-medium' : 'text-gray-600 hover:text-black'
                }`}
                onClick={() => setIsMenuOpen(false)}
              >
                Healing Rooms
                {isUsingHealingRooms && (
                  <div className="ml-2 w-1 h-4 bg-black rounded-full"></div>
                )}
              </Link>
              <Link
                href="/exterior-spaces"
                className={`py-2 transition-colors duration-300 flex items-center ${
                  isUsingExteriorSpaces ? 'text-black font-medium' : 'text-gray-600 hover:text-black'
                }`}
                onClick={() => setIsMenuOpen(false)}
              >
                Exterior Spaces
                {isUsingExteriorSpaces && (
                  <div className="ml-2 w-1 h-4 bg-black rounded-full"></div>
                )}
              </Link>
              <Link
                href="https://www.thinkround.org/aboutus"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-600 hover:text-black py-2 transition-colors duration-300"
                onClick={() => setIsMenuOpen(false)}
              >
                About
              </Link>
              <Link
                href="https://thinkround.shop/"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-600 hover:text-black py-2 transition-colors duration-300"
                onClick={() => setIsMenuOpen(false)}
              >
                Shop
              </Link>
              <Link
                href="https://www.thinkround.org/donate"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-600 hover:text-black py-2 transition-colors duration-300 flex items-center"
                onClick={() => setIsMenuOpen(false)}
              >
                <Heart className="w-4 h-4 mr-2" />
                Donate
              </Link>
              
              <div className="pt-3 border-t border-gray-100 space-y-2">
                {isAuthenticated ? (
                  <>
                    <Link href="/chat" onClick={() => setIsMenuOpen(false)}>
                      <Button className="w-full bg-black hover:bg-gray-800 text-white rounded-full">
                        Chat
                      </Button>
                    </Link>
                    <Button 
                      variant="outline" 
                      className="w-full text-red-600 hover:bg-red-50"
                      onClick={() => {
                        setIsMenuOpen(false);
                        handleLogout();
                      }}
                    >
                      Sign Out
                    </Button>
                  </>
                ) : (
                  <Button 
                    className="w-full bg-black hover:bg-gray-800 text-white rounded-full"
                    onClick={(e) => {
                      setIsMenuOpen(false);
                      handleLogin(e);
                    }}
                  >
                    Get Started
                  </Button>
                )}
              </div>
            </div>
          </div>
        )}
      </nav>
    </header>
  );
}
