"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { auth, db } from "@/app/lib/firebase";
import { signOut } from "firebase/auth";
import { doc, getDoc } from "firebase/firestore";
import { useAuth } from "@/app/context/AuthContext";

import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
  TooltipProvider,
} from "@/components/ui/tooltip";
import { Menu, Bell, FileUp, LogOut, User as UserIcon } from "lucide-react";

export default function MainHeader() {
  const { user, loading } = useAuth();
  const router = useRouter();

  const [initials, setInitials] = useState<string>("?");
  const [fullName, setFullName] = useState<string>("User");

  // Fetch User Data from Firestore for Initials and Name
  useEffect(() => {
    const fetchUserData = async () => {
      if (user?.uid) {
        try {
          const docRef = doc(db, "users", user.uid);
          const docSnap = await getDoc(docRef);

          if (docSnap.exists()) {
            const data = docSnap.data();
            const fName = data.firstName || "";
            const lName = data.lastName || "";

            setFullName(`${fName} ${lName}`.trim());

            // Get first letter of first name and last name
            const init = `${fName.charAt(0)}${lName.charAt(0)}`.toUpperCase();
            setInitials(init || "U");
          }
        } catch (error) {
          console.error("Error fetching user data:", error);
        }
      }
    };

    fetchUserData();
  }, [user]);

  const handleSignOut = async () => {
    try {
      await signOut(auth);
      router.push("/authentication/login"); // Redirect to login after logout
    } catch (error) {
      console.error("Error signing out:", error);
    }
  };

  // Prevent header from flashing wrong state while checking auth
  if (loading) return null;

  return (
    <header
      className="
        fixed top-2 left-1/2 -translate-x-1/2 w-[95%] md:w-[80%] lg:w-[65%] 
        border border-border rounded-2xl 
        bg-background/40 backdrop-blur-md 
        z-50 shadow-sm
      "
    >
      <div className="max-w-7xl mx-auto px-4 h-16 flex justify-between items-center">
        {/* Logo */}
        <Link
          href="/"
          className="font-bold text-xl tracking-tight text-primary"
        >
          FEDERx
        </Link>

        {/* Right Section */}
        {user ? (
          // ==============================
          // AUTHENTICATED STATE
          // ==============================
          <div className="flex gap-2 items-center">
            {/* --- Desktop Icons (Hidden on small screens) --- */}
            <div className="hidden md:flex items-center gap-2 mr-2">
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="hover:bg-primary/10"
                      asChild
                    >
                      <Link href="/mainpages/uploadpage">
                        <FileUp className="h-5 w-5" />
                      </Link>
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent side="bottom">Uploads</TooltipContent>
                </Tooltip>

                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="hover:bg-primary/10"
                      asChild
                    >
                      <Link href="/notifications">
                        <Bell className="h-5 w-5" />
                      </Link>
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent side="bottom">Notifications</TooltipContent>
                </Tooltip>
              </TooltipProvider>
            </div>

            {/* --- Profile Dropdown (Desktop & Mobile) --- */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button
                  variant="outline"
                  className="rounded-full h-10 w-10 p-0 bg-primary/10 border-primary/30 hover:bg-primary/20 text-primary font-bold transition-all"
                >
                  {initials}
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-56 mt-2">
                <DropdownMenuLabel className="font-normal">
                  <div className="flex flex-col space-y-1">
                    <p className="text-sm font-medium leading-none">
                      {fullName}
                    </p>
                    <p className="text-xs leading-none text-muted-foreground">
                      {user.email}
                    </p>
                  </div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />

                {/* Mobile only menu items */}
                <div className="md:hidden">
                  <DropdownMenuItem asChild>
                    <Link
                      href="/mainpages/uploadpage"
                      className="cursor-pointer"
                    >
                      <FileUp className="mr-2 h-4 w-4" /> Uploads
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem asChild>
                    <Link href="/notifications" className="cursor-pointer">
                      <Bell className="mr-2 h-4 w-4" /> Notifications
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                </div>

                <DropdownMenuItem asChild>
                  <Link
                    href="/mainpages/profilepage"
                    className="cursor-pointer"
                  >
                    <UserIcon className="mr-2 h-4 w-4" /> Profile
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem
                  onClick={handleSignOut}
                  className="text-red-500 focus:text-red-500 cursor-pointer"
                >
                  <LogOut className="mr-2 h-4 w-4" />
                  Sign out
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        ) : (
          // ==============================
          // UNAUTHENTICATED STATE
          // ==============================
          <div className="flex items-center gap-2">
            <div className="hidden md:flex gap-2">
              <Button variant="ghost" asChild>
                <Link href="/login">Log in</Link>
              </Button>
              <Button asChild>
                <Link href="/signup">Sign up</Link>
              </Button>
            </div>

            {/* Mobile Hamburger for Logged Out */}
            <div className="md:hidden">
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" size="icon">
                    <Menu className="h-5 w-5" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-40">
                  <DropdownMenuItem asChild>
                    <Link href="/login" className="w-full cursor-pointer">
                      Log in
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem asChild>
                    <Link href="/signup" className="w-full cursor-pointer">
                      Sign up
                    </Link>
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>
        )}
      </div>
    </header>
  );
}
