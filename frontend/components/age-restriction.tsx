import { AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";
import Link from "next/link";

export default function AgeRestriction() {
  return (
    <div className="bg-white rounded-xl p-8 shadow-xl">
      <div className="flex flex-col items-center justify-center text-center">
        <AlertTriangle className="h-16 w-16 text-red-500 mb-4" />
        <h1 className="text-2xl font-bold text-red-600 mb-4">
          Age Restriction
        </h1>
        <p className="text-gray-700 mb-6 text-lg">
          ⚠️ You must be 18 years or older to use this assistant.
        </p>
        <p className="text-amber-600 font-medium mb-8">
          Session ended due to age restrictions.
        </p>
        <Link href="/">
          <Button className="bg-gradient-to-r from-blue-500 to-cyan-600 hover:from-blue-600 hover:to-cyan-700 text-white shadow-lg hover:shadow-blue-500/25 transition-all duration-300">
            Return to Homepage
          </Button>
        </Link>
      </div>
    </div>
  );
}
