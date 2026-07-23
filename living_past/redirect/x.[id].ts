// The Living Past — stable QR redirect endpoint (SCOPE §8).
// Deploy to the live site as: site/src/pages/x/[id].ts
// A printed QR encodes jrk.art/x/<ID> (e.g. /x/CR14). This 301s to the current
// page. Restructure the site freely — only redirects.json changes; codes never die.
//
// Copy living_past/redirect/redirects.json to site/src/data/redirects.json when
// wiring this into the live site.
import type { APIRoute } from "astro";
import redirects from "../../data/redirects.json";

type Entry = { slug: string; path: string; volume: string };
const TABLE = redirects as Record<string, Entry>;

// Fallback if an ID isn't mapped yet (new print, page not built): send to the
// volume index rather than a dead 404.
const VOLUME_INDEX: Record<string, string> = { V: "/late-cretaceous" };

export const GET: APIRoute = ({ params, redirect }) => {
  const id = (params.id ?? "").toUpperCase();
  const entry = TABLE[id];
  if (entry) return redirect(entry.path, 301);

  const vol = id.slice(0, 2) === "CR" ? "V" : "";
  return redirect(VOLUME_INDEX[vol] ?? "/", 302);
};

export function getStaticPaths() {
  // Pre-render every known ID so the redirects are static/CDN-fast.
  return Object.keys(TABLE).map((id) => ({ params: { id } }));
}
