type Hotel = {
  id: string;
  name: string;
  location_id: number;
  created_at: string;
  updated_at: string | null;
  deleted_at: string | null;
  action: "CREATE" | "UPDATE" | "DELETE";
};

async function fetchHotels(): Promise<Hotel[]> {
  const baseUrl = process.env.NEXT_PUBLIC_API_URL;
  if (!baseUrl) {
    throw new Error("NEXT_PUBLIC_API_URL is not set");
  }

  const response = await fetch(`${baseUrl}/hotels`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error("Failed to fetch hotels");
  }

  return response.json();
}

export default async function Home() {
  const hotels = await fetchHotels();

  return (
    <div className="flex min-h-screen items-center justify-center bg-zinc-50 font-sans dark:bg-black">
      <main className="flex min-h-screen w-full max-w-3xl flex-col gap-8 py-24 px-16 bg-white dark:bg-black">
        <header className="space-y-2">
          <h1 className="text-3xl font-semibold tracking-tight text-black dark:text-zinc-50">
            Hotels
          </h1>
          <p className="text-base text-zinc-600 dark:text-zinc-400">
            A basic list of hotels created in the database.
          </p>
        </header>

        {hotels.length === 0 ? (
          <p className="text-lg text-zinc-600 dark:text-zinc-400">
            No hotels created
          </p>
        ) : (
          <ul className="space-y-3 text-lg text-black dark:text-zinc-50">
            {hotels.map((hotel) => (
              <li key={hotel.id} className="rounded border border-zinc-200 p-4 dark:border-zinc-800">
                <div className="font-medium">{hotel.name}</div>
                <div className="text-sm text-zinc-500 dark:text-zinc-400">
                  Location ID: {hotel.location_id}
                </div>
              </li>
            ))}
          </ul>
        )}
      </main>
    </div>
  );
}
