"use client";

import { Button } from "@/components/ui/button";
import {
  Field,
  FieldDescription,
  FieldGroup,
  FieldLabel,
  FieldLegend,
  FieldSet,
} from "@/components/ui/field";
import { Spinner } from "@/components/ui/spinner";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import Link from "next/link";
import Image from "next/image";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { Eye, EyeOff, AlertCircle, Sparkles } from "lucide-react";

// NEW: Import Firebase Auth functions
import { signInWithEmailAndPassword, sendSignInLinkToEmail } from "firebase/auth";
import { auth } from "@/app/lib/firebase";

type formDataType = {
  email: string;
  password: string;
};

export default function LoginPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [otpLogin, setOtpLogin] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null); // NEW: For email sent status
  const [showPassword, setShowPassword] = useState<{ show: boolean }>({
    show: false,
  });
  const [formData, setFormData] = useState<formDataType>({
    email: "",
    password: "",
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  // UPDATED: Firebase login handler
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccessMsg(null);
    setIsLoading(true);

    try {
      if (otpLogin) {
        // --- EMAIL LINK (MAGIC LINK) LOGIN FLOW ---
        const actionCodeSettings = {
          // URL you want to redirect back to. Must be whitelisted in Firebase Console.
          url: `${window.location.origin}/`, 
          handleCodeInApp: true,
        };

        await sendSignInLinkToEmail(auth, formData.email, actionCodeSettings);
        
        // Save email locally so we don't have to ask for it again when they click the link
        window.localStorage.setItem('emailForSignIn', formData.email);
        setSuccessMsg("A verification link has been sent to your email!");
        
      } else {
        // --- PASSWORD LOGIN FLOW ---
        if (formData.password.length < 6) {
          setError("Password must be at least 6 characters.");
          setIsLoading(false);
          return;
        }

        await signInWithEmailAndPassword(auth, formData.email, formData.password);
        
        // Note: If you set up the AuthContext from the previous step, 
        // it will automatically intercept this and redirect to "/". 
        // We include this push as a fallback.
        router.push("/");
      }
    } catch (err: any) {
      console.error("Login error:", err);
      
      // Friendly error mapping
      switch (err.code) {
        case "auth/invalid-credential":
          setError("Invalid email or password. Please try again.");
          break;
        case "auth/user-not-found":
          setError("No account found with this email.");
          break;
        case "auth/too-many-requests":
          setError("Too many failed attempts. Please try again later.");
          break;
        default:
          setError(err.message || "An unexpected error occurred.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen flex flex-col items-center justify-center bg-background px-4 py-12 overflow-hidden">
      
      {/* Background Orbs & Grid */}
      <div className="absolute top-[-10%] left-[-10%] w-[50vw] h-[50vw] bg-primary opacity-20 blur-[120px] rounded-full pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[40vw] h-[40vw] bg-primary opacity-10 blur-[100px] rounded-full pointer-events-none" />
      <div className="absolute inset-0 z-0 pointer-events-none bg-[linear-gradient(to_right,#80808020_1px,transparent_1px),linear-gradient(to_bottom,#80808020_1px,transparent_1px)] bg-[size:32px_32px] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_50%,#000_60%,transparent_100%)]" />

      {/* Header */}
      <div className="relative z-10 flex flex-col items-center text-center mb-10">
        <div className="bg-primary/10 p-3 rounded-2xl mb-4 text-primary">
          <Sparkles className="w-10 h-10" />
        </div>
        <h1 className="text-3xl md:text-5xl font-bold text-foreground tracking-tight">
          Welcome Back
        </h1>
        <p className="text-muted-foreground mt-3 text-md md:text-xl max-w-md">
          Sign in to continue collaborating with excellence
        </p>
      </div>

      {/* Main Content Card */}
      <div className="relative z-10 w-full max-w-5xl flex flex-col lg:flex-row items-stretch justify-center rounded-2xl overflow-hidden shadow-2xl border border-border bg-card/50 backdrop-blur-xl">
        
        <Card className="w-full lg:w-1/2 p-6 md:p-10 bg-transparent border-none flex flex-col justify-center">
          <form className="flex flex-col w-full" onSubmit={handleSubmit}>
            
            {/* Error State */}
            {error && (
              <Alert variant="destructive" className="mb-6">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            {/* Success State for Email Link */}
            {successMsg && (
              <Alert className="mb-6 border-green-500 text-green-600 bg-green-50">
                <Sparkles className="h-4 w-4" color="green" />
                <AlertDescription>{successMsg}</AlertDescription>
              </Alert>
            )}

            <FieldGroup>
              <FieldSet className="space-y-6">
                <div className="mb-2 text-center lg:text-left">
                  <FieldLegend>
                    <h2 className="text-xl md:text-2xl font-semibold">
                      {otpLogin ? "Login using Email Link" : "Login using Password"}
                    </h2>
                  </FieldLegend>
                  <FieldDescription className="text-sm md:text-base mt-1">
                    {otpLogin 
                      ? "A magic link will be sent to your registered email address" 
                      : "Enter your credentials to access your account"}
                  </FieldDescription>
                </div>

                <div className="space-y-4">
                  <Field className="space-y-2">
                    <FieldLabel htmlFor="email" className="font-medium">
                      Email Address
                    </FieldLabel>
                    <Input
                      name="email"
                      id="email"
                      placeholder="example@gmail.com"
                      value={formData.email}
                      onChange={handleChange}
                      required
                      type="email"
                      className="bg-background/50 border-border hover:bg-muted/50 transition-colors"
                    />
                  </Field>

                  {/* Only show password field if NOT in OTP mode */}
                  {!otpLogin && (
                    <Field className="space-y-2 w-full">
                      <FieldLabel htmlFor="password" className="font-medium">
                        Password
                      </FieldLabel>
                      <div className="relative">
                        <Input
                          name="password"
                          id="password"
                          type={showPassword.show ? "text" : "password"}
                          value={formData.password}
                          onChange={handleChange}
                          placeholder="Enter your Password"
                          required={!otpLogin}
                          className="bg-background/50 border-border hover:bg-muted/50 transition-colors pr-10"
                        />
                        <button
                          type="button"
                          onClick={() =>
                            setShowPassword((prev) => ({ show: !prev.show }))
                          }
                          className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                          aria-label={showPassword.show ? "Hide password" : "Show password"}
                        >
                          {showPassword.show ? (
                            <EyeOff className="h-4 w-4" />
                          ) : (
                            <Eye className="h-4 w-4" />
                          )}
                        </button>
                      </div>
                    </Field>
                  )}
                </div>
              </FieldSet>

              {/* Submit & Toggle Buttons */}
              <div className="flex flex-col items-center mt-6 space-y-4">
                <Button
                  type="submit"
                  className="w-3/4 p-4 hover:bg-primary/90"
                  disabled={isLoading || !!successMsg}
                >
                  {isLoading ? (
                    <span className="flex gap-2 items-center justify-center">
                      <Spinner className="w-5 h-5" /> Submitting...
                    </span>
                  ) : otpLogin ? (
                    "Send Magic Link"
                  ) : (
                    "Sign In"
                  )}
                </Button>

                <Button
                  type="button"
                  className="w-3/4 hover:bg-primary/5 bg-background/50"
                  variant="outline"
                  onClick={() => {
                    setOtpLogin(!otpLogin);
                    setError(null);
                    setSuccessMsg(null);
                  }}
                  disabled={isLoading}
                >
                  {otpLogin ? "Sign In using Password" : "Sign In using Email Link"}
                </Button>

                <p className="text-sm md:text-base text-muted-foreground mt-4">
                  Don’t have an account?{" "}
                  <Link
                    href="/signup"
                    className="text-primary font-medium hover:underline underline-offset-4"
                  >
                    Sign up
                  </Link>
                </p>
              </div>
            </FieldGroup>
          </form>
        </Card>

        {/* Right Side Illustration */}
        <div className="w-full lg:w-1/2 relative min-h-[400px] lg:min-h-[500px] overflow-hidden shadow-xl hidden md:block">
          <Image
            src="/login.png"
            alt="Login Illustration"
            fill
            className="object-cover"
            priority
          />
        </div>
      </div>
    </div>
  );
}