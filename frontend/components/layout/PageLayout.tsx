import type { ReactNode } from "react";

import { Sidebar } from "@/components/layout/Sidebar";
import { TopBar } from "@/components/layout/TopBar";

type PageLayoutProps = {
  activeRoute: "dashboard" | "ticket";
  children: ReactNode;
};

export function PageLayout({ activeRoute, children }: PageLayoutProps) {
  return (
    <>
      <TopBar />
      <div className="mx-auto flex max-w-[1600px] flex-col pt-16 lg:flex-row">
        <Sidebar activeRoute={activeRoute} />
        <main className="min-w-0 flex-1 p-4 sm:p-6">{children}</main>
      </div>
    </>
  );
}
