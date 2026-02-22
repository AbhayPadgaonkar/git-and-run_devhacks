"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { db } from "@/app/lib/firebase";
import {
  collection,
  query,
  where,
  onSnapshot,
  updateDoc,
  doc,
  getDoc,
  Timestamp,
} from "firebase/firestore";
import { useAuth } from "@/app/context/AuthContext";
import { Spinner } from "@/components/ui/spinner";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Empty,
  EmptyContent,
  EmptyDescription,
  EmptyHeader,
  EmptyMedia,
  EmptyTitle,
} from "@/components/ui/empty";
import { CheckCircle2, XCircle, Mail, Clock, ArrowLeft } from "lucide-react";

type Invitation = {
  id: string;
  experimentId: string;
  experimentName: string;
  adminEmail: string;
  clientEmail: string;
  status: "pending" | "accepted" | "rejected";
  createdAt: any;
  respondedAt?: any;
};

export default function NotificationsPage() {
  const { user } = useAuth();
  const router = useRouter();
  const [invitations, setInvitations] = useState<Invitation[]>([]);
  const [loading, setLoading] = useState(true);
  const [userRole, setUserRole] = useState("");

  useEffect(() => {
    const fetchUserRole = async () => {
      if (!user?.uid) return;

      const userDoc = await getDoc(doc(db, "users", user.uid));
      if (userDoc.exists()) {
        setUserRole(userDoc.data().role || "");
      }
    };

    fetchUserRole();
  }, [user?.uid]);

  useEffect(() => {
    if (!user?.email || !userRole) {
      setLoading(false);
      return;
    }

    const invitationsRef = collection(db, "invitations");
    const q = query(invitationsRef, where("clientEmail", "==", user.email));

    const unsubscribe = onSnapshot(q, (snapshot) => {
      const invitationsData: Invitation[] = [];
      snapshot.forEach((doc) => {
        invitationsData.push({ id: doc.id, ...doc.data() } as Invitation);
      });
      // Sort by createdAt, newest first
      invitationsData.sort((a, b) => {
        const aTime = a.createdAt?.toMillis?.() || 0;
        const bTime = b.createdAt?.toMillis?.() || 0;
        return bTime - aTime;
      });
      setInvitations(invitationsData);
      setLoading(false);
    });

    return () => unsubscribe();
  }, [user?.email, userRole]);

  const handleInvitationResponse = async (
    invitationId: string,
    experimentId: string,
    status: "accepted" | "rejected",
  ) => {
    try {
      const invitationRef = doc(db, "invitations", invitationId);
      await updateDoc(invitationRef, {
        status,
        respondedAt: Timestamp.now(),
      });

      if (status === "accepted") {
        // Update experiment client count
        const experimentRef = doc(db, "experiments", experimentId);
        const experimentDoc = await getDoc(experimentRef);

        if (experimentDoc.exists()) {
          const currentCount = experimentDoc.data().clientsEnrolled || 0;
          await updateDoc(experimentRef, {
            clientsEnrolled: currentCount + 1,
          });
        }
      }

      alert(`Invitation ${status}!`);
    } catch (error) {
      console.error("Error responding to invitation:", error);
      alert("Failed to respond to invitation");
    }
  };

  const formatTimestamp = (timestamp: any) => {
    if (!timestamp) return "N/A";
    const date = timestamp.toDate ? timestamp.toDate() : new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return "just now";
    if (diffMins < 60) return `${diffMins} mins ago`;
    if (diffHours < 24) return `${diffHours} hours ago`;
    return `${diffDays} days ago`;
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <Spinner />
      </div>
    );
  }

  return (
    <div className="relative min-h-screen bg-background text-foreground overflow-hidden">
      {/* Background Effects */}
      <div className="fixed inset-0 z-0 pointer-events-none flex justify-center">
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808025_1px,transparent_1px),linear-gradient(to_bottom,#80808025_1px,transparent_1px)] bg-[size:40px_40px]" />
        <div className="absolute top-[-10%] w-[80vw] h-[50vh] bg-primary/20 blur-[120px] rounded-[100%] mix-blend-normal" />
      </div>

      {/* Main Content */}
      <main className="relative z-10 max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 mt-20 space-y-6">
        {/* Header */}
        <div className="flex items-center gap-4">
          <Button
            variant="outline"
            size="icon"
            onClick={() => router.push("/home")}
          >
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold tracking-tight flex items-center gap-3">
              <Mail className="h-8 w-8 text-primary" />
              Notifications
            </h1>
            <p className="text-muted-foreground mt-1">
              Manage your project invitations
            </p>
          </div>
        </div>

        {/* Pending Invitations */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>Pending Invitations</span>
              <Badge variant="secondary">
                {invitations.filter((inv) => inv.status === "pending").length}
              </Badge>
            </CardTitle>
            <CardDescription>
              Accept or decline project invitations from admins
            </CardDescription>
          </CardHeader>
          <CardContent>
            {invitations.filter((inv) => inv.status === "pending").length >
            0 ? (
              <div className="space-y-3">
                {invitations
                  .filter((inv) => inv.status === "pending")
                  .map((invitation) => (
                    <div
                      key={invitation.id}
                      className="flex flex-col sm:flex-row sm:items-center justify-between p-4 border border-violet-200 rounded-lg bg-violet-50/30 gap-4"
                    >
                      <div className="flex-1">
                        <p className="font-semibold text-lg">
                          {invitation.experimentName}
                        </p>
                        <p className="text-sm text-muted-foreground">
                          Invited by {invitation.adminEmail}
                        </p>
                        <p className="text-xs text-muted-foreground mt-1">
                          {formatTimestamp(invitation.createdAt)}
                        </p>
                      </div>
                      <div className="flex gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() =>
                            handleInvitationResponse(
                              invitation.id,
                              invitation.experimentId,
                              "rejected",
                            )
                          }
                        >
                          <XCircle className="mr-1 h-3 w-3" />
                          Decline
                        </Button>
                        <Button
                          size="sm"
                          className="bg-violet-700 hover:bg-violet-800"
                          onClick={() =>
                            handleInvitationResponse(
                              invitation.id,
                              invitation.experimentId,
                              "accepted",
                            )
                          }
                        >
                          <CheckCircle2 className="mr-1 h-3 w-3" />
                          Accept
                        </Button>
                      </div>
                    </div>
                  ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <Empty>
                  <EmptyHeader>
                    <EmptyMedia variant="icon">
                      <Mail />
                    </EmptyMedia>
                    <EmptyTitle className="font-semibold text-xl">
                      No Pending Invitations
                    </EmptyTitle>
                    <EmptyDescription>
                      You&apos;re all caught up! New invitations will appear
                      here.
                    </EmptyDescription>
                  </EmptyHeader>
                </Empty>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Past Responses */}
        {invitations.filter((inv) => inv.status !== "pending").length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Past Responses</CardTitle>
              <CardDescription>
                History of accepted and declined invitations
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {invitations
                  .filter((inv) => inv.status !== "pending")
                  .map((invitation) => (
                    <div
                      key={invitation.id}
                      className="flex items-center justify-between p-4 border rounded-lg"
                    >
                      <div>
                        <p className="font-medium">
                          {invitation.experimentName}
                        </p>
                        <p className="text-sm text-muted-foreground">
                          From {invitation.adminEmail}
                        </p>
                        <p className="text-xs text-muted-foreground mt-1">
                          Responded {formatTimestamp(invitation.respondedAt)}
                        </p>
                      </div>
                      <Badge
                        variant={
                          invitation.status === "accepted"
                            ? "default"
                            : "destructive"
                        }
                      >
                        {invitation.status === "accepted" && (
                          <CheckCircle2 className="mr-1 h-3 w-3" />
                        )}
                        {invitation.status === "rejected" && (
                          <XCircle className="mr-1 h-3 w-3" />
                        )}
                        {invitation.status}
                      </Badge>
                    </div>
                  ))}
              </div>
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  );
}
