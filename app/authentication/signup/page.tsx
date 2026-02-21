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
import {
  Eye,
  EyeOff,
  AlertCircle,
  Sparkles,
  User,
  ShieldCheck,
} from "lucide-react";

// Database Imports
import { auth, db } from "@/database/firebase";
import { createUserWithEmailAndPassword } from "firebase/auth";
import { doc, setDoc } from "firebase/firestore";

type formDataType = {
  firstName: string;
  lastName: string;
  email: string;
  password: string;
  confirmPassword: string;
  role: "admin" | "client";
};

export default function SignupPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showPassword, setShowPassword] = useState(false);

  const [formData, setFormData] = useState<formDataType>({
    firstName: "",
    lastName: "",
    email: "",
    password: "",
    confirmPassword: "",
    role: "client",
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === "radio" ? value : value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      // 1. Create user in Auth

      if (formData.password !== formData.confirmPassword) {
        setError("Passwords do not match. Please try again.");
        setIsLoading(false);
        return;
      }

      if (formData.password.length < 6) {
        setError("Password must be at least 6 characters.");
        setIsLoading(false);
        return;
      }


      const userCredential = await createUserWithEmailAndPassword(
        auth,
        formData.email.trim(),
        formData.password,
      );

      const user = userCredential.user;
      console.log("Auth User Created:", user.uid);

      // 2. Save to Firestore
      // Wrapping this in a try-catch specifically to see if DB is the bottleneck
      try {
        await setDoc(doc(db, "users", user.uid), {
          firstName: formData.firstName,
          lastName: formData.lastName,
          email: formData.email.toLowerCase().trim(),
          role: formData.role,
          createdAt: new Date().toISOString(),
        });
        console.log("Firestore Profile Created");
      } catch (dbError: any) {
        console.error("Firestore Error:", dbError);
        // We don't want to stop the user if DB fails, but we should know why
        throw new Error(
          "Account created, but profile setup failed. Please contact support.",
        );
      }

      // 3. Force Redirect
      // Use window.location.href if router.push is being ignored by the middleware
      window.location.href = "/home";
    } catch (err: any) {
      console.error("General Signup Error:", err.code, err.message);
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen flex flex-col items-center justify-center bg-background px-4 py-12 overflow-hidden">
      {/* Background Decorations */}
      <div className="absolute top-[-10%] left-[-10%] w-[50vw] h-[50vw] bg-primary opacity-20 blur-[120px] rounded-full pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[40vw] h-[40vw] bg-primary opacity-10 blur-[100px] rounded-full pointer-events-none" />
      <div className="absolute inset-0 z-0 pointer-events-none bg-[linear-gradient(to_right,#80808020_1px,transparent_1px),linear-gradient(to_bottom,#80808020_1px,transparent_1px)] bg-[size:32px_32px] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_50%,#000_60%,transparent_100%)]" />

      {/* Header */}
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

      <div className="relative z-10 w-full max-w-5xl flex flex-col lg:flex-row items-stretch justify-center rounded-2xl overflow-hidden shadow-2xl border border-border bg-card/50 backdrop-blur-xl">
        <Card className="w-full lg:w-1/2 p-6 md:p-8 bg-transparent border-none flex flex-col justify-center">
          {/* Submit handled here */}
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
                    Fill in your details below
                  </FieldDescription>
                </div>

                {/* Role Selection */}
                <div className="grid grid-cols-2 gap-4 mb-4">
                  <label
                    className={`cursor-pointer rounded-lg border p-4 flex flex-col items-center gap-2 transition-all ${formData.role === "client" ? "border-primary bg-primary/10" : "border-border bg-background/50 hover:bg-muted"}`}
                  >
                    <input
                      type="radio"
                      name="role"
                      value="client"
                      checked={formData.role === "client"}
                      onChange={handleChange}
                      className="sr-only"
                    />
                    <User
                      className={
                        formData.role === "client"
                          ? "text-primary"
                          : "text-muted-foreground"
                      }
                      size={24}
                    />
                    <span
                      className={`font-semibold text-sm ${formData.role === "client" ? "text-primary" : "text-muted-foreground"}`}
                    >
                      Edge Client
                    </span>
                  </label>

                  <label
                    className={`cursor-pointer rounded-lg border p-4 flex flex-col items-center gap-2 transition-all ${formData.role === "admin" ? "border-primary bg-primary/10" : "border-border bg-background/50 hover:bg-muted"}`}
                  >
                    <input
                      type="radio"
                      name="role"
                      value="admin"
                      checked={formData.role === "admin"}
                      onChange={handleChange}
                      className="sr-only"
                    />
                    <ShieldCheck
                      className={
                        formData.role === "admin"
                          ? "text-primary"
                          : "text-muted-foreground"
                      }
                      size={24}
                    />
                    <span
                      className={`font-semibold text-sm ${formData.role === "admin" ? "text-primary" : "text-muted-foreground"}`}
                    >
                      System Admin
                    </span>
                  </label>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <Field className="space-y-2">
                    <FieldLabel htmlFor="firstName">First Name</FieldLabel>
                    <Input
                      name="firstName"
                      id="firstName"
                      placeholder="John"
                      value={formData.firstName}
                      onChange={handleChange}
                      required
                    />
                  </Field>
                  <Field className="space-y-2">
                    <FieldLabel htmlFor="lastName">Last Name</FieldLabel>
                    <Input
                      name="lastName"
                      id="lastName"
                      placeholder="Doe"
                      value={formData.lastName}
                      onChange={handleChange}
                      required
                    />
                  </Field>
                </div>

                <Field className="space-y-2">
                  <FieldLabel htmlFor="email">Email Address</FieldLabel>
                  <Input
                    type="email"
                    name="email"
                    id="email"
                    placeholder="example@company.com"
                    value={formData.email}
                    onChange={handleChange}
                    required
                  />
                </Field>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Field className="space-y-2">
                    <FieldLabel htmlFor="password">Password</FieldLabel>
                    <div className="relative">
                      <Input
                        name="password"
                        id="password"
                        type={showPassword ? "text" : "password"}
                        value={formData.password}
                        onChange={handleChange}
                        required
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground"
                      >
                        {showPassword ? (
                          <EyeOff size={16} />
                        ) : (
                          <Eye size={16} />
                        )}
                      </button>
                    </div>
                  </Field>

                  <Field className="space-y-2">
                    <FieldLabel htmlFor="confirmPassword">Confirm</FieldLabel>
                    <Input
                      name="confirmPassword"
                      id="confirmPassword"
                      type={showPassword ? "text" : "password"}
                      value={formData.confirmPassword}
                      onChange={handleChange}
                      required
                    />
                  </Field>
                </div>
              </FieldSet>

              <div className="flex flex-col items-center mt-6 space-y-4">
                <Button
                  type="submit"
                  className="w-full p-4"
                  disabled={isLoading}
                >
                  {isLoading ? (
                    <>
                      <Spinner className="w-5 h-5 mr-2" /> Creating...
                    </>
                  ) : (
                    "Create Account"
                  )}
                </Button>

                <p className="text-sm text-muted-foreground">
                  Already have an account?{" "}
                  <Link
                    href="/authentication/login"
                    className="text-primary hover:underline"
                  >
                    Log In
                  </Link>
                </p>
              </div>
            </FieldGroup>
          </form>
        </Card>

        <div className="w-full lg:w-1/2 relative min-h-[400px] hidden md:block border-l border-border/50">
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
