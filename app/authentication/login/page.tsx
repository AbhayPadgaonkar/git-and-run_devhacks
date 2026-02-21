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
import { Eye, EyeOff, AlertCircle, Sparkles } from "lucide-react"; // Added a placeholder logo icon

type formDataType = {
  email: string;
  password: string;
};

export default function LoginPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [otpLogin, setOtpLogin] = useState(false);
  const [error, setError] = useState<string | null>(null);
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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    if (formData.password.length < 6) {
      setError("Password must be at least 6 characters.");
      setIsLoading(false);
      return;
    }

    // Redirect to the Details Page
    router.push("/mainpages/dashboard");
  };
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-background px-4 py-12">
      {/* Top Heading & Logo Section */}
      <div className="flex flex-col items-center text-center mb-10">
        <div className="bg-primary/10 p-3 rounded-2xl mb-4 text-primary">
          {/* Replace this Sparkles icon with your actual Logo/Image component */}
          <Sparkles className="w-10 h-10" />
        </div>
        <h1 className="text-3xl md:text-5xl font-bold text-foreground tracking-tight">
          Welcome Back
        </h1>
        <p className="text-muted-foreground mt-3 text-md md:text-xl max-w-md">
          Sign in to continue collaborating with excellence
        </p>
      </div>

      {/* Main Content Wrapper */}
      <div className="w-full max-w-5xl flex flex-col lg:flex-row items-stretch justify-center  rounded-2xl overflow-hidden shadow-xl border border-border  bg-muted/30">
        {/* LEFT: Form Card */}
        <Card className="w-full lg:w-1/2 p-6 md:p-10 bg-card border-none flex flex-col justify-center ">
          {otpLogin ? (
            <form className="flex flex-col w-full" onSubmit={handleSubmit}>
              {error && (
                <Alert variant="destructive" className="mb-6">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              <FieldGroup>
                <FieldSet className="space-y-6">
                  <div className="mb-2 text-center lg:text-left">
                    <FieldLegend>
                      <h2 className="text-xl md:text-2xl font-semibold">
                        Login using OTP
                      </h2>
                    </FieldLegend>
                    <FieldDescription className="text-sm md:text-base mt-1">
                      An OTP will be sent to your registered email address
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
                        className="bg-background border-border hover:bg-muted/50 transition-colors"
                      />
                    </Field>
                  </div>
                </FieldSet>

                {/* Submit & Redirect Section */}
                <div className="flex flex-col items-center mt-4 space-y-4">
                  <Button
                    className="w-3/4 p-4 hover:bg-primary/90"
                    disabled={isLoading}
                  >
                    {isLoading ? (
                      <span className="flex gap-2 items-center justify-center">
                        <Spinner className="w-5 h-5" /> Submitting...
                      </span>
                    ) : (
                      "Send verification email"
                    )}
                  </Button>
                  <Button
                    className="w-3/4 hover:bg-primary/5"
                    variant={"outline"}
                    onClick={() => setOtpLogin(false)}
                    disabled={isLoading}
                  >
                    {isLoading ? (
                      <span className="flex gap-2 items-center justify-center">
                        <Spinner className="w-5 h-5" /> Submitting...
                      </span>
                    ) : (
                      "Sign In using Email"
                    )}
                  </Button>
                  <p className="text-sm md:text-base text-muted-foreground mt-4">
                    Don’t have an account?{" "}
                    <Link
                      href="/signuppage"
                      className="text-primary font-medium hover:underline underline-offset-4"
                    >
                      Sign up
                    </Link>
                  </p>
                </div>
              </FieldGroup>
            </form>
          ) : (
            <form className="flex flex-col w-full" onSubmit={handleSubmit}>
              {error && (
                <Alert variant="destructive" className="mb-6">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}
              <FieldGroup>
                <FieldSet className="space-y-6">
                  <div className="mb-2 text-center lg:text-left">
                    <FieldLegend>
                      <h2 className="text-xl md:text-2xl font-semibold">
                        Login using Password
                      </h2>
                    </FieldLegend>
                    <FieldDescription className="text-sm md:text-base mt-1">
                      Enter correct password to login
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
                        className="bg-background border-border hover:bg-muted/50 transition-colors"
                      />
                    </Field>

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
                          required
                          className="bg-background border-border hover:bg-muted/50 transition-colors pr-10"
                        />
                        <button
                          type="button"
                          onClick={() =>
                            setShowPassword((prev) => ({ show: !prev.show }))
                          }
                          className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                          aria-label={
                            showPassword.show
                              ? "Hide password"
                              : "Show password"
                          }
                        >
                          {showPassword.show ? (
                            <EyeOff className="h-4 w-4" />
                          ) : (
                            <Eye className="h-4 w-4" />
                          )}
                        </button>
                      </div>
                    </Field>
                  </div>
                </FieldSet>

                {/* Submit & Redirect Section */}
                <div className="flex flex-col items-center mt-4 space-y-4">
                  <Button
                    className="w-3/4 p-4 hover:bg-primary/90"
                    disabled={isLoading}
                  >
                    {isLoading ? (
                      <span className="flex gap-2 items-center justify-center">
                        <Spinner className="w-5 h-5" /> Submitting...
                      </span>
                    ) : (
                      "Sign In"
                    )}
                  </Button>
                  <Button
                    className="w-3/4 hover:bg-primary/5"
                    variant={"outline"}
                    onClick={() => setOtpLogin(true)}
                    disabled={isLoading}
                  >
                    {isLoading ? (
                      <span className="flex gap-2 items-center justify-center">
                        <Spinner className="w-5 h-5" /> Submitting...
                      </span>
                    ) : (
                      "Sign In using OTP"
                    )}
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
          )}
        </Card>

        {/* RIGHT: Image Container */}
        <div className="w-full lg:w-1/2 relative min-h-[400px] lg:min-h-[500px]  overflow-hidden shadow-xl hidden md:block bg-muted/30">
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
