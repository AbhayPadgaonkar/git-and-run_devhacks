"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { db } from "@/app/lib/firebase";
import {
  doc,
  getDoc,
  collection,
  query,
  where,
  getDocs,
  addDoc,
  updateDoc,
  Timestamp,
  onSnapshot,
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
import { Progress } from "@/components/ui/progress";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Activity,
  Users,
  Mail,
  ArrowLeft,
  TrendingUp,
  Clock,
  Network,
  Shield,
  CheckCircle2,
  XCircle,
  AlertTriangle,
} from "lucide-react";

type Experiment = {
  id: string;
  name: string;
  description: string;
  modelType: string;
  status: string;
  currentRound: number;
  totalRounds: number;
  currentAccuracy: number;
  currentLoss: number;
  clientsEnrolled: number;
  aggregationMethod: string;
  enableTrust: boolean;
  requireAdminReview: boolean;
  autoApproveThreshold: number;
  minClientsPerRound: number;
  maxStaleness: number;
  targetAccuracy: number;
  createdBy: string;
  createdAt: any;
  lastUpdated: any;
};

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

type UserData = {
  email: string;
  firstName: string;
  lastName: string;
  role: string;
};

export default function DashboardPage() {
  const params = useParams();
  const router = useRouter();
  const { user } = useAuth();
  const experimentId = params.experimentId as string;

  const [experiment, setExperiment] = useState<Experiment | null>(null);
  const [userRole, setUserRole] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [inviteDialogOpen, setInviteDialogOpen] = useState(false);
  const [inviteEmail, setInviteEmail] = useState("");
  const [inviting, setInviting] = useState(false);
  const [invitations, setInvitations] = useState<Invitation[]>([]);
  const [clientInvitations, setClientInvitations] = useState<Invitation[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      if (!user?.uid) return;

      try {
        setLoading(true);

        // Fetch user role
        const userDoc = await getDoc(doc(db, "users", user.uid));
        if (userDoc.exists()) {
          setUserRole(userDoc.data().role || "");
        }

        // Fetch experiment
        const expDoc = await getDoc(doc(db, "experiments", experimentId));
        if (expDoc.exists()) {
          setExperiment({ id: expDoc.id, ...expDoc.data() } as Experiment);
        }
      } catch (error) {
        console.error("Error fetching data:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [user?.uid, experimentId]);

  // Real-time invitations listener for admin
  useEffect(() => {
    if (!user?.email || userRole !== "admin") return;

    const invitationsRef = collection(db, "invitations");
    const q = query(invitationsRef, where("experimentId", "==", experimentId));

    const unsubscribe = onSnapshot(q, (snapshot) => {
      const invitationsData: Invitation[] = [];
      snapshot.forEach((doc) => {
        invitationsData.push({ id: doc.id, ...doc.data() } as Invitation);
      });
      setInvitations(invitationsData);
    });

    return () => unsubscribe();
  }, [user?.email, userRole, experimentId]);

  // Real-time invitations listener for client
  useEffect(() => {
    if (!user?.email || userRole !== "client") return;

    const invitationsRef = collection(db, "invitations");
    const q = query(
      invitationsRef,
      where("clientEmail", "==", user.email),
      where("experimentId", "==", experimentId),
    );

    const unsubscribe = onSnapshot(q, (snapshot) => {
      const invitationsData: Invitation[] = [];
      snapshot.forEach((doc) => {
        invitationsData.push({ id: doc.id, ...doc.data() } as Invitation);
      });
      setClientInvitations(invitationsData);
    });

    return () => unsubscribe();
  }, [user?.email, userRole, experimentId]);

  const handleInviteClient = async () => {
    if (!inviteEmail.trim() || !experiment) {
      alert("Please enter a valid email");
      return;
    }

    try {
      setInviting(true);

      // Check if user exists and is a client
      const usersRef = collection(db, "users");
      const q = query(usersRef, where("email", "==", inviteEmail));
      const querySnapshot = await getDocs(q);

      if (querySnapshot.empty) {
        alert("User with this email does not exist");
        return;
      }

      const userData = querySnapshot.docs[0].data();
      if (userData.role !== "client") {
        alert("User is not a client");
        return;
      }

      // Check if invitation already exists
      const invitationsRef = collection(db, "invitations");
      const existingQuery = query(
        invitationsRef,
        where("experimentId", "==", experimentId),
        where("clientEmail", "==", inviteEmail),
      );
      const existingInvitations = await getDocs(existingQuery);

      if (!existingInvitations.empty) {
        alert("Invitation already sent to this client");
        return;
      }

      // Create invitation
      await addDoc(collection(db, "invitations"), {
        experimentId,
        experimentName: experiment.name,
        adminEmail: user?.email,
        clientEmail: inviteEmail,
        status: "pending",
        createdAt: Timestamp.now(),
      });

      setInviteEmail("");
      setInviteDialogOpen(false);
      alert("Invitation sent successfully!");
    } catch (error) {
      console.error("Error inviting client:", error);
      alert("Failed to send invitation");
    } finally {
      setInviting(false);
    }
  };

  const handleInvitationResponse = async (
    invitationId: string,
    status: "accepted" | "rejected",
  ) => {
    try {
      const invitationRef = doc(db, "invitations", invitationId);
      await updateDoc(invitationRef, {
        status,
        respondedAt: Timestamp.now(),
      });

      if (status === "accepted" && experiment) {
        // Update experiment with new client count
        const experimentRef = doc(db, "experiments", experimentId);
        await updateDoc(experimentRef, {
          clientsEnrolled: experiment.clientsEnrolled + 1,
        });
      }

      alert(`Invitation ${status}!`);
    } catch (error) {
      console.error("Error responding to invitation:", error);
      alert("Failed to respond to invitation");
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <Spinner />
      </div>
    );
  }

  if (!experiment) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen">
        <p className="text-lg text-muted-foreground mb-4">
          Experiment not found
        </p>
        <Button onClick={() => router.push("/home")}>
          <ArrowLeft className="mr-2 h-4 w-4" /> Back to Projects
        </Button>
      </div>
    );
  }

  // Admin Dashboard
  if (userRole === "admin") {
    return (
      <div className="relative min-h-screen bg-background text-foreground overflow-hidden">
        {/* Background Effects */}
        <div className="fixed inset-0 z-0 pointer-events-none flex justify-center">
          <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808025_1px,transparent_1px),linear-gradient(to_bottom,#80808025_1px,transparent_1px)] bg-[size:40px_40px]" />
          <div className="absolute top-[-10%] w-[80vw] h-[50vh] bg-primary/20 blur-[120px] rounded-[100%] mix-blend-normal" />
          <div className="absolute bottom-[-10%] w-[80vw] h-[50vh] bg-primary/10 blur-[150px] rounded-[100%] mix-blend-normal" />
        </div>

        {/* Main Content */}
        <main className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 mt-20 space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between">
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
                  <Activity className="h-8 w-8 text-primary" />
                  {experiment.name}
                </h1>
                <p className="text-muted-foreground mt-1">
                  Admin Dashboard · {experiment.modelType} Model
                </p>
              </div>
            </div>

            <Dialog open={inviteDialogOpen} onOpenChange={setInviteDialogOpen}>
              <DialogTrigger asChild>
                <Button className="bg-violet-700 hover:bg-violet-800 text-white">
                  <Mail className="mr-2 h-4 w-4" /> Invite Client
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Invite Client to Project</DialogTitle>
                  <DialogDescription>
                    Enter the email address of the client you want to invite to
                    this experiment.
                  </DialogDescription>
                </DialogHeader>
                <div className="grid gap-4 py-4">
                  <div className="grid gap-2">
                    <Label htmlFor="email">Client Email</Label>
                    <Input
                      id="email"
                      type="email"
                      value={inviteEmail}
                      onChange={(e) => setInviteEmail(e.target.value)}
                      placeholder="client@example.com"
                    />
                  </div>
                </div>
                <DialogFooter>
                  <Button
                    variant="outline"
                    onClick={() => setInviteDialogOpen(false)}
                  >
                    Cancel
                  </Button>
                  <Button
                    onClick={handleInviteClient}
                    disabled={inviting}
                    className="bg-violet-700 hover:bg-violet-800"
                  >
                    {inviting ? "Sending..." : "Send Invitation"}
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Status
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-2">
                  <Badge
                    variant="secondary"
                    className="bg-violet-100 text-violet-700"
                  >
                    <Activity className="mr-1 h-3 w-3" />
                    {experiment.status}
                  </Badge>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Clients Enrolled
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {experiment.clientsEnrolled}
                </div>
                <p className="text-xs text-muted-foreground">
                  Min: {experiment.minClientsPerRound} per round
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Current Accuracy
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {(experiment.currentAccuracy * 100).toFixed(1)}%
                </div>
                <p className="text-xs text-muted-foreground">
                  Target: {(experiment.targetAccuracy * 100).toFixed(0)}%
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Training Progress
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {experiment.currentRound}/{experiment.totalRounds}
                </div>
                <Progress
                  value={
                    (experiment.currentRound / experiment.totalRounds) * 100
                  }
                  className="mt-2 h-2"
                />
              </CardContent>
            </Card>
          </div>

          {/* Experiment Details & Invitations */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Experiment Configuration */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Shield className="h-5 w-5 text-primary" />
                  Experiment Configuration
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-muted-foreground">
                      Aggregation Method
                    </p>
                    <p className="font-medium">
                      {experiment.aggregationMethod}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Model Type</p>
                    <p className="font-medium">{experiment.modelType}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">
                      Max Staleness
                    </p>
                    <p className="font-medium">
                      {experiment.maxStaleness} rounds
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">
                      Current Loss
                    </p>
                    <p className="font-medium">
                      {experiment.currentLoss.toFixed(4)}
                    </p>
                  </div>
                </div>
                <div className="flex gap-4 pt-2">
                  <div className="flex items-center gap-2">
                    <div
                      className={`h-2 w-2 rounded-full ${experiment.enableTrust ? "bg-green-500" : "bg-gray-300"}`}
                    />
                    <span className="text-sm">Trust Scoring</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div
                      className={`h-2 w-2 rounded-full ${experiment.requireAdminReview ? "bg-green-500" : "bg-gray-300"}`}
                    />
                    <span className="text-sm">Admin Review</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Invitations Panel */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Users className="h-5 w-5 text-primary" />
                  Client Invitations
                  <Badge variant="secondary" className="ml-auto">
                    {invitations.length}
                  </Badge>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3 max-h-64 overflow-y-auto">
                  {invitations.length > 0 ? (
                    invitations.map((invitation) => (
                      <div
                        key={invitation.id}
                        className="flex items-center justify-between p-3 border rounded-lg"
                      >
                        <div>
                          <p className="font-medium text-sm">
                            {invitation.clientEmail}
                          </p>
                          <p className="text-xs text-muted-foreground">
                            {invitation.createdAt
                              ?.toDate?.()
                              .toLocaleDateString()}
                          </p>
                        </div>
                        <Badge
                          variant={
                            invitation.status === "accepted"
                              ? "default"
                              : invitation.status === "rejected"
                                ? "destructive"
                                : "secondary"
                          }
                        >
                          {invitation.status === "accepted" && (
                            <CheckCircle2 className="mr-1 h-3 w-3" />
                          )}
                          {invitation.status === "rejected" && (
                            <XCircle className="mr-1 h-3 w-3" />
                          )}
                          {invitation.status === "pending" && (
                            <Clock className="mr-1 h-3 w-3" />
                          )}
                          {invitation.status}
                        </Badge>
                      </div>
                    ))
                  ) : (
                    <div className="text-center py-8 text-muted-foreground">
                      <Users className="h-12 w-12 mx-auto mb-2 opacity-20" />
                      <p className="text-sm">No invitations sent yet</p>
                      <p className="text-xs">
                        Click "Invite Client" to get started
                      </p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Description */}
          {experiment.description && (
            <Card>
              <CardHeader>
                <CardTitle>Description</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">
                  {experiment.description}
                </p>
              </CardContent>
            </Card>
          )}
        </main>
      </div>
    );
  }

  // Client Dashboard
  return (
    <div className="relative min-h-screen bg-background text-foreground overflow-hidden">
      {/* Background Effects */}
      <div className="fixed inset-0 z-0 pointer-events-none flex justify-center">
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808025_1px,transparent_1px),linear-gradient(to_bottom,#80808025_1px,transparent_1px)] bg-[size:40px_40px]" />
        <div className="absolute top-[-10%] w-[80vw] h-[50vh] bg-primary/15 blur-[120px] rounded-[100%] mix-blend-normal" />
        <div className="absolute bottom-[-10%] w-[80vw] h-[50vh] bg-primary/10 blur-[150px] rounded-[100%] mix-blend-normal" />
      </div>

      {/* Main Content */}
      <main className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 mt-20 space-y-6">
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
              <Activity className="h-8 w-8 text-primary" />
              {experiment.name}
            </h1>
            <p className="text-muted-foreground mt-1">
              Client Dashboard · Contribute to Federated Learning
            </p>
          </div>
        </div>

        {/* Invitation Requests */}
        {clientInvitations.length > 0 && (
          <Card className="border-violet-200 bg-violet-50/50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-violet-900">
                <Mail className="h-5 w-5" />
                Project Invitations
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {clientInvitations.map((invitation) => (
                <div
                  key={invitation.id}
                  className="flex items-center justify-between p-4 bg-white border border-violet-200 rounded-lg"
                >
                  <div>
                    <p className="font-medium">
                      Invited by {invitation.adminEmail}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      {invitation.createdAt?.toDate?.().toLocaleDateString()}
                    </p>
                  </div>
                  {invitation.status === "pending" ? (
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() =>
                          handleInvitationResponse(invitation.id, "rejected")
                        }
                      >
                        <XCircle className="mr-1 h-3 w-3" />
                        Decline
                      </Button>
                      <Button
                        size="sm"
                        className="bg-violet-700 hover:bg-violet-800"
                        onClick={() =>
                          handleInvitationResponse(invitation.id, "accepted")
                        }
                      >
                        <CheckCircle2 className="mr-1 h-3 w-3" />
                        Accept
                      </Button>
                    </div>
                  ) : (
                    <Badge
                      variant={
                        invitation.status === "accepted"
                          ? "default"
                          : "destructive"
                      }
                    >
                      {invitation.status}
                    </Badge>
                  )}
                </div>
              ))}
            </CardContent>
          </Card>
        )}

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Project Status
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Badge
                variant="secondary"
                className="bg-violet-100 text-violet-700"
              >
                <Activity className="mr-1 h-3 w-3" />
                {experiment.status}
              </Badge>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Total Clients
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {experiment.clientsEnrolled}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Model Accuracy
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {(experiment.currentAccuracy * 100).toFixed(1)}%
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Round Progress
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {experiment.currentRound}/{experiment.totalRounds}
              </div>
              <Progress
                value={(experiment.currentRound / experiment.totalRounds) * 100}
                className="mt-2 h-2"
              />
            </CardContent>
          </Card>
        </div>

        {/* Project Information */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Network className="h-5 w-5 text-primary" />
              Project Information
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {experiment.description && (
              <div>
                <p className="text-sm text-muted-foreground mb-1">
                  Description
                </p>
                <p>{experiment.description}</p>
              </div>
            )}
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              <div>
                <p className="text-sm text-muted-foreground">Model Type</p>
                <p className="font-medium">{experiment.modelType}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Aggregation</p>
                <p className="font-medium">{experiment.aggregationMethod}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Target Accuracy</p>
                <p className="font-medium">
                  {(experiment.targetAccuracy * 100).toFixed(0)}%
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
