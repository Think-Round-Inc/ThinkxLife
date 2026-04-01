import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function CTA() {
  return (
    <section className="py-20 px-6 md:px-12 lg:px-24 bg-purple-700 text-white">
      <div className="max-w-4xl mx-auto text-center">
        <h2 className="text-3xl md:text-4xl font-bold mb-6">
          Get in Touch with Think Round, Inc
        </h2>
        <p className="text-lg mb-10 opacity-90">
          Have questions about our programs or want to get involved? Our AI
          assistant can help you connect with us.
        </p>
        <div className="flex flex-col sm:flex-row justify-center gap-4">
          <Link href="/healing-rooms">
            <Button className="bg-white text-purple-700 hover:bg-gray-100 px-8 py-3 rounded-md text-lg">
              Healing Rooms
            </Button>
          </Link>
          <Link href="https://www.thinkround.org/donate">
            <Button className="bg-green-600 hover:bg-green-700 text-white px-8 py-3 rounded-md text-lg">
              Donate
            </Button>
          </Link>
        </div>
      </div>
    </section>
  );
}
