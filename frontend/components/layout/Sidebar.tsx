import Link from "next/link";

type SidebarProps = {
  activeRoute: "dashboard" | "ticket";
};

const links = [
  { label: "OPERATIONS", href: "/", route: "dashboard" },
  { label: "TICKET DETAIL", href: "/tickets/demo-001", route: "ticket" },
] as const;

export function Sidebar({ activeRoute }: SidebarProps) {
  return (
    <aside className="w-full shrink-0 border-b border-hairline pb-4 lg:sticky lg:top-20 lg:h-[calc(100vh-5rem)] lg:w-52 lg:border-b-0 lg:border-r lg:pb-0">
      <nav className="flex gap-2 px-4 pt-4 lg:flex-col lg:px-3" aria-label="Operations navigation">
        {links.map((link) => {
          const active = link.route === activeRoute;
          return (
            <Link
              key={link.href}
              href={link.href}
              className={`border px-3 py-2 font-mono text-[10px] tracking-[0.12em] transition-colors ${
                active
                  ? "border-hairline-bright bg-panel-raised text-text"
                  : "border-transparent text-text-faint hover:border-hairline hover:text-text-muted"
              }`}
            >
              {link.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
