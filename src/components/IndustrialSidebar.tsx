"use client";

import React, { useState } from "react";
import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { cn } from "@/lib/utils";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  LayoutDashboard,
  Rss,
  Globe,
  Settings,
  List,
  PlayCircle,
  CalendarClock,
  ChevronsUpDown,
  Blocks,
  FileClock,
  GraduationCap,
  Layout,
  MessageSquareText,
  Plus,
  UserCircle,
  Wrench,
  Factory,
  Cog,
  BarChart3,
  FileText,
} from "lucide-react";

const sidebarVariants = {
  open: {
    width: "15rem",
  },
  closed: {
    width: "3.05rem",
  },
};

const contentVariants = {
  open: { display: "block", opacity: 1 },
  closed: { display: "block", opacity: 1 },
};

const variants = {
  open: {
    x: 0,
    opacity: 1,
    transition: {
      x: { stiffness: 1000, velocity: -100 },
    },
  },
  closed: {
    x: -20,
    opacity: 0,
    transition: {
      x: { stiffness: 100 },
    },
  },
};

const transitionProps = {
  type: "tween",
  ease: "easeOut",
  duration: 0.2,
  staggerChildren: 0.1,
};

const staggerVariants = {
  open: {
    transition: { staggerChildren: 0.03, delayChildren: 0.02 },
  },
};

interface SectionProps {
  title: string;
  links: {
    label: string;
    href: string;
    icon: React.ReactNode;
    badge?: string;
  }[];
}

/**
 * IndustrialSidebar component provides a collapsible sidebar navigation for the app.
 *
 * - Expands on hover, collapses otherwise
 * - Contains navigation sections and links
 * - Uses Framer Motion for smooth transitions
 */
export function IndustrialSidebar() {
  const [isCollapsed, setIsCollapsed] = useState(true);
  const pathname = "/dashboard"; // This would normally come from usePathname()

  const sections: SectionProps[] = [
    {
      title: "Main",
      links: [
        {
          label: "Dashboard",
          href: "/dashboard",
          icon: <LayoutDashboard className="h-4 w-4" />,
        },
        {
          label: "RSS Feed",
          href: "/rss-feed",
          icon: <Rss className="h-4 w-4" />,
        },
        {
          label: "Web Feed",
          href: "/web-feed",
          icon: <Globe className="h-4 w-4" />,
        },
        {
          label: "Notes",
          href: "/notes",
          icon: <FileText className="h-4 w-4" />,
        },
      ],
    },
    {
      title: "Management",
      links: [
        {
          label: "Preferences",
          href: "/preferences",
          icon: <Settings className="h-4 w-4" />,
        },
        {
          label: "RSS Sources",
          href: "/rss-sources",
          icon: <List className="h-4 w-4" />,
        },
        {
          label: "RSS Runs",
          href: "/rss-runs",
          icon: <PlayCircle className="h-4 w-4" />,
        },
        {
          label: "Scheduler",
          href: "/scheduler",
          icon: <CalendarClock className="h-4 w-4" />,
        },
      ],
    },
  ];

  return (
    <motion.div
      className={cn(
        "sidebar fixed left-0 z-40 h-full shrink-0 border-r fixed"
      )}
      initial={isCollapsed ? "closed" : "open"}
      animate={isCollapsed ? "closed" : "open"}
      variants={sidebarVariants}
      transition={transitionProps}
      onMouseEnter={() => setIsCollapsed(false)}
      onMouseLeave={() => setIsCollapsed(true)}
    >
      <motion.div
        className={`relative z-40 flex text-muted-foreground h-full shrink-0 flex-col bg-zinc-900 dark:bg-zinc-900 transition-all`}
        variants={contentVariants}
      >
        <motion.ul variants={staggerVariants} className="flex h-full flex-col">
          <div className="flex grow flex-col items-center">
            <div className="flex h-[54px] w-full shrink-0 border-b border-zinc-800 p-2">
              <div className="mt-[1.5px] flex w-full">
                <DropdownMenu modal={false}>
                  <DropdownMenuTrigger className="w-full" asChild>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="flex w-fit items-center gap-2 px-2 text-zinc-300"
                    >
                      <Avatar className="rounded size-4 bg-zinc-700">
                        <AvatarFallback className="text-zinc-300">I</AvatarFallback>
                      </Avatar>
                      <motion.li
                        variants={variants}
                        className="flex w-fit items-center gap-2"
                      >
                        {!isCollapsed && (
                          <>
                            <p className="text-sm font-medium">
                              Industrial Systems
                            </p>
                            <ChevronsUpDown className="h-4 w-4 text-muted-foreground/50" />
                          </>
                        )}
                      </motion.li>
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="start" className="bg-zinc-800 text-zinc-300 border-zinc-700">
                    <DropdownMenuItem
                      className="flex items-center gap-2 hover:bg-zinc-700"
                    >
                      <Link to="/settings/members">
                        <UserCircle className="h-4 w-4" /> Manage members
                      </Link>
                    </DropdownMenuItem>
                    <DropdownMenuItem
                      className="flex items-center gap-2 hover:bg-zinc-700"
                    >
                      <Link to="/settings/integrations">
                        <Blocks className="h-4 w-4" /> Integrations
                      </Link>
                    </DropdownMenuItem>
                    <DropdownMenuItem className="hover:bg-zinc-700">
                      <Link
                        to="/select-org"
                        className="flex items-center gap-2"
                      >
                        <Plus className="h-4 w-4" />
                        Create new organization
                      </Link>
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            </div>

            <div className="flex h-full w-full flex-col">
              <div className="flex grow flex-col gap-4">
                <ScrollArea className="h-16 grow p-2">
                  <div className={cn("flex w-full flex-col gap-1")}> 
                    {sections.map((section, sectionIndex) => (
                      <div key={sectionIndex} className="mb-4">
                        {!isCollapsed && (
                          <h3 className="text-xs font-semibold text-zinc-500 mb-2 px-2">
                            {section.title}
                          </h3>
                        )}
                        {section.links.map((link, linkIndex) => (
                          <Link
                            key={linkIndex}
                            to={link.href}
                            className={cn(
                              "flex h-8 w-full flex-row items-center rounded-md px-2 py-1.5 transition hover:bg-zinc-800 hover:text-zinc-200",
                              pathname?.includes(link.href.substring(1)) &&
                                "bg-zinc-800 text-zinc-200"
                            )}
                          >
                            <div className="text-zinc-400">{link.icon}</div>
                            <motion.li variants={variants}>
                              {!isCollapsed && (
                                <div className="ml-2 flex items-center gap-2">
                                  <p className="text-base font-medium">{link.label}</p>
                                  {link.badge && (
                                    <Badge
                                      className={cn(
                                        "flex h-fit w-fit items-center gap-1.5 rounded border-none bg-zinc-700 px-1.5 text-zinc-300"
                                      )}
                                      variant="outline"
                                    >
                                      {link.badge}
                                    </Badge>
                                  )}
                                </div>
                              )}
                            </motion.li>
                          </Link>
                        ))}
                        {sectionIndex < sections.length - 1 && !isCollapsed && (
                          <Separator className="my-3 bg-zinc-800" />
                        )}
                      </div>
                    ))}
                  </div>
                </ScrollArea>
              </div>
              <div className="flex flex-col p-2">
                <Link
                  to="/settings"
                  className="mt-auto flex h-8 w-full flex-row items-center rounded-md px-2 py-1.5 transition hover:bg-zinc-800 hover:text-zinc-200"
                >
                  <Cog className="h-4 w-4 shrink-0 text-zinc-400" />
                  <motion.li variants={variants}>
                    {!isCollapsed && (
                      <p className="ml-2 text-sm font-medium">Settings</p>
                    )}
                  </motion.li>
                </Link>
                <div>
                  <DropdownMenu modal={false}>
                    <DropdownMenuTrigger className="w-full">
                      <div className="flex h-8 w-full flex-row items-center gap-2 rounded-md px-2 py-1.5 transition hover:bg-zinc-800 hover:text-zinc-200">
                        <Avatar className="size-4 bg-zinc-700">
                          <AvatarFallback className="text-zinc-300">
                            U
                          </AvatarFallback>
                        </Avatar>
                        <motion.li
                          variants={variants}
                          className="flex w-full items-center gap-2"
                        >
                          {!isCollapsed && (
                            <>
                              <p className="text-sm font-medium">User Account</p>
                              <ChevronsUpDown className="ml-auto h-4 w-4 text-muted-foreground/50" />
                            </>
                          )}
                        </motion.li>
                      </div>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent sideOffset={5} className="bg-zinc-800 text-zinc-300 border-zinc-700">
                      <div className="flex flex-row items-center gap-2 p-2">
                        <Avatar className="size-6 bg-zinc-700">
                          <AvatarFallback className="text-zinc-300">
                            UA
                          </AvatarFallback>
                        </Avatar>
                        <div className="flex flex-col text-left">
                          <span className="text-sm font-medium">
                            User Account
                          </span>
                          <span className="line-clamp-1 text-xs text-muted-foreground">
                            user@industrial.com
                          </span>
                        </div>
                      </div>
                      <DropdownMenuSeparator className="bg-zinc-700" />
                      <DropdownMenuItem
                        className="flex items-center gap-2 hover:bg-zinc-700"
                      >
                        <Link to="/settings/profile">
                          <UserCircle className="h-4 w-4" /> Profile
                        </Link>
                      </DropdownMenuItem>
                      <DropdownMenuItem
                        className="flex items-center gap-2 hover:bg-zinc-700"
                      >
                        <Link to="/settings/signout">
                          <UserCircle className="h-4 w-4" /> Sign out
                        </Link>
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              </div>
            </div>
          </div>
        </motion.ul>
      </motion.div>
    </motion.div>
  );
} 