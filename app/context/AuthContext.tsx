"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import { onAuthStateChanged, User } from "firebase/auth";
import { auth } from "../lib/firebase";
import { useRouter, usePathname } from "next/navigation";
import { Spinner } from "@/components/ui/spinner"; // Assuming you have this

interface AuthContextType {
  user: User | null;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType>({ user: null, loading: true });

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
      setUser(currentUser);
      setLoading(false);

      // Redirect logic
      if (currentUser && (pathname === "/authentication/signup" || pathname === "/authentication/login")) {
        router.push("/"); // Redirect to Home if logged in and on an auth page
      } 
    });

    return () => unsubscribe();
  }, [pathname, router]);

  if (loading) {
    return <div className="h-screen w-full flex items-center justify-center"><Spinner className="w-8 h-8" /></div>;
  }

  return (
    <AuthContext.Provider value={{ user, loading }}>
      {children}
    </AuthContext.Provider>
  );
};