import Link from "next/link";
import Image from "next/image";
import { Button } from "@/components/ui/button";

export default function Hero() {
  return (
    <section className="relative pt-16 pb-24 px-6 md:px-12 lg:px-24 overflow-hidden">
      <div className="max-w-6xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
          <div>
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-6 text-gray-800">
              Earth is home. <br />
              <span className="text-purple-700">Humans are family.</span>
            </h1>

            <p className="text-lg text-gray-600 mb-8">
              Think Round, Inc is a non-profit organization dedicated to
              promoting arts, education, and community engagement. We believe in
              the power of creativity to connect people and foster
              understanding.
            </p>

            <div className="flex flex-col sm:flex-row gap-4">
              <Link href="/healing-rooms">
                <Button className="bg-purple-700 hover:bg-purple-800 text-white px-8 py-3 rounded-md">
                  Healing Rooms
                </Button>
              </Link>
            </div>
          </div>

          <div className="relative">
            <div className="rounded-full bg-gradient-to-r from-purple-200 to-blue-200 p-1">
              <Image
                src="/colorful-globe-diverse-people.png"
                alt="Think Round Inc"
                width={500}
                height={500}
                className="rounded-full"
              />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
