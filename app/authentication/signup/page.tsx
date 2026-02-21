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
import { Eye, EyeOff, AlertCircle, Sparkles, User, ShieldCheck } from "lucide-react";

type formDataType = {
  firstName: string;
  lastName: string;
  id: string; // Used for email or username
  password: string;
  confirmPassword: string;
  role: "admin" | "client";
};

export default function SignupPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showPassword, setShowPassword] = useState<{ show: boolean }>({
    show: false,
  });
  
  const [formData, setFormData] = useState<formDataType>({
    firstName: "",
    lastName: "",
    id: "",
    password: "",
    confirmPassword: "",
    role: "client", // default selection
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type } = e.target;
    
    // Handle radio button selection specifically
    if (type === "radio") {
      setFormData((prev) => ({
        ...prev,
        role: value as "admin" | "client",
      }));
    } else {
      setFormData((prev) => ({
        ...prev,
        [name]: value,
      }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    if (formData.password.length < 6) {
      setError("Password must be at least 6 characters.");
      setIsLoading(false);
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      setError("Passwords do not match.");
      setIsLoading(false);
      return;
    }

    // Simulate API call delay
    setTimeout(() => {
      // Redirect based on selected role
      if (formData.role === "admin") {
        router.push("/admin/dashboard");
      } else {
        router.push("/client/dashboard");
      }
    }, 1000);
  };

  return (
    <div className="relative min-h-screen flex flex-col items-center justify-center bg-background px-4 py-12 overflow-hidden">
      
      {/* ========================================================= */}
      {/* THE NEW BACKGROUND GRADIENTS & GRID (Highly Visible)      */}
      {/* ========================================================= */}
      
      {/* Top Left Primary Glowing Orb */}
      <div className="absolute top-[-10%] left-[-10%] w-[50vw] h-[50vw] bg-primary opacity-20 blur-[120px] rounded-full pointer-events-none" />
      
      {/* Bottom Right Secondary Glowing Orb */}
      <div className="absolute bottom-[-10%] right-[-10%] w-[40vw] h-[40vw] bg-primary opacity-10 blur-[100px] rounded-full pointer-events-none" />
      
      {/* Enterprise Tech Grid Overlay */}
      <div className="absolute inset-0 z-0 pointer-events-none bg-[linear-gradient(to_right,#80808020_1px,transparent_1px),linear-gradient(to_bottom,#80808020_1px,transparent_1px)] bg-[size:32px_32px] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_50%,#000_60%,transparent_100%)]" />

      {/* ========================================================= */}

      {/* Top Heading & Logo Section */}
      <div className="relative z-10 flex flex-col items-center text-center mb-10">
        <div className="bg-primary/10 p-3 rounded-2xl mb-4 text-primary">
          <Sparkles className="w-10 h-10" />
        </div>
        <h1 className="text-3xl md:text-5xl font-bold text-foreground tracking-tight">
          Join FederX
        </h1>
        <p className="text-muted-foreground mt-3 text-md md:text-xl max-w-md">
          Create an account to deploy and collaborate securely
        </p>
      </div>

      {/* Main Content Wrapper */}
      <div className="relative z-10 w-full max-w-5xl flex flex-col lg:flex-row items-stretch justify-center rounded-2xl overflow-hidden shadow-2xl border border-border bg-card/50 backdrop-blur-xl">
        
        {/* LEFT: Form Card */}
        <Card className="w-full lg:w-1/2 p-6 md:p-8 bg-transparent border-none flex flex-col justify-center">
          <form className="flex flex-col w-full" onSubmit={handleSubmit}>
            {error && (
              <Alert variant="destructive" className="mb-6">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            <FieldGroup>
              <FieldSet className="space-y-4">
                <div className="mb-2 text-center lg:text-left">
                  <FieldLegend>
                    <h2 className="text-xl md:text-2xl font-semibold">
                      Create your account
                    </h2>
                  </FieldLegend>
                  <FieldDescription className="text-sm mt-1">
                    Fill in your details below to get started
                  </FieldDescription>
                </div>

                {/* Role Selection (Radio Buttons styled as Cards) */}
                <div className="grid grid-cols-2 gap-4 mb-4">
                  {/* Client Role Option */}
                  <label className={`cursor-pointer rounded-lg border p-4 flex flex-col items-center gap-2 transition-all ${formData.role === 'client' ? 'border-primary bg-primary/10' : 'border-border bg-background/50 hover:bg-muted'}`}>
                    <input 
                      type="radio" 
                      name="role" 
                      value="client" 
                      checked={formData.role === 'client'}
                      onChange={handleChange}
                      className="sr-only" 
                    />
                    <User className={formData.role === 'client' ? 'text-primary' : 'text-muted-foreground'} size={24} />
                    <span className={`font-semibold text-sm ${formData.role === 'client' ? 'text-primary' : 'text-muted-foreground'}`}>Edge Client</span>
                  </label>

                  {/* Admin Role Option */}
                  <label className={`cursor-pointer rounded-lg border p-4 flex flex-col items-center gap-2 transition-all ${formData.role === 'admin' ? 'border-primary bg-primary/10' : 'border-border bg-background/50 hover:bg-muted'}`}>
                    <input 
                      type="radio" 
                      name="role" 
                      value="admin" 
                      checked={formData.role === 'admin'}
                      onChange={handleChange}
                      className="sr-only" 
                    />
                    <ShieldCheck className={formData.role === 'admin' ? 'text-primary' : 'text-muted-foreground'} size={24} />
                    <span className={`font-semibold text-sm ${formData.role === 'admin' ? 'text-primary' : 'text-muted-foreground'}`}>System Admin</span>
                  </label>
                </div>

                {/* Name Fields (Side by Side) */}
                <div className="grid grid-cols-2 gap-4">
                  <Field className="space-y-2">
                    <FieldLabel htmlFor="firstName" className="font-medium">First Name</FieldLabel>
                    <Input
                      name="firstName"
                      id="firstName"
                      placeholder="John"
                      value={formData.firstName}
                      onChange={handleChange}
                      required
                      className="bg-background/50 border-border hover:bg-muted/50 transition-colors"
                    />
                  </Field>
                  <Field className="space-y-2">
                    <FieldLabel htmlFor="lastName" className="font-medium">Last Name</FieldLabel>
                    <Input
                      name="lastName"
                      id="lastName"
                      placeholder="Doe"
                      value={formData.lastName}
                      onChange={handleChange}
                      required
                      className="bg-background/50 border-border hover:bg-muted/50 transition-colors"
                    />
                  </Field>
                </div>

                {/* ID/Email Field */}
                <Field className="space-y-2">
                  <FieldLabel htmlFor="id" className="font-medium">Federation ID or Email</FieldLabel>
                  <Input
                    name="id"
                    id="id"
                    placeholder="example@company.com"
                    value={formData.id}
                    onChange={handleChange}
                    required
                    className="bg-background/50 border-border hover:bg-muted/50 transition-colors"
                  />
                </Field>

                {/* Password Fields (Side by Side) */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Field className="space-y-2">
                    <FieldLabel htmlFor="password" className="font-medium">Password</FieldLabel>
                    <div className="relative">
                      <Input
                        name="password"
                        id="password"
                        type={showPassword.show ? "text" : "password"}
                        value={formData.password}
                        onChange={handleChange}
                        placeholder="••••••••"
                        required
                        className="bg-background/50 border-border hover:bg-muted/50 transition-colors pr-10"
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword((prev) => ({ show: !prev.show }))}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                      >
                        {showPassword.show ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                      </button>
                    </div>
                  </Field>

                  <Field className="space-y-2">
                    <FieldLabel htmlFor="confirmPassword" className="font-medium">Confirm Password</FieldLabel>
                    <Input
                      name="confirmPassword"
                      id="confirmPassword"
                      type={showPassword.show ? "text" : "password"}
                      value={formData.confirmPassword}
                      onChange={handleChange}
                      placeholder="••••••••"
                      required
                      className="bg-background/50 border-border hover:bg-muted/50 transition-colors"
                    />
                  </Field>
                </div>
              </FieldSet>

              {/* Submit & Redirect Section */}
              <div className="flex flex-col items-center mt-6 space-y-4">
                <Button
                  className="w-full p-4 hover:bg-primary/90"
                  disabled={isLoading}
                >
                  {isLoading ? (
                    <span className="flex gap-2 items-center justify-center">
                      <Spinner className="w-5 h-5" /> Creating account...
                    </span>
                  ) : (
                    "Create Account"
                  )}
                </Button>

                <p className="text-sm md:text-base text-muted-foreground mt-4">
                  Already have an account?{" "}
                  <Link
                    href="/authentication/login"
                    className="text-primary font-medium hover:underline underline-offset-4"
                  >
                    Log In
                  </Link>
                </p>
              </div>
            </FieldGroup>
          </form>
        </Card>

        {/* RIGHT: Image Container (Updated to signup.jpeg) */}
        <div className="w-full lg:w-1/2 relative min-h-[400px] lg:min-h-auto overflow-hidden shadow-xl hidden md:block border-l border-border/50">
          <Image
            src="/signup.jpeg"
            alt="Signup Illustration"
            fill
            className="object-cover"
            priority
          />
        </div>
      </div>
    </div>
  );
}