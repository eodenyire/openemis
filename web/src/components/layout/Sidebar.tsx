"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import {
  LayoutDashboard, Users, UserCheck, DollarSign, CalendarCheck,
  BookOpen, FileBarChart, Settings, Menu, X, GraduationCap,
  Bell, MessageSquare, ClipboardList, Activity, Award,
  Building2, ShieldAlert, Briefcase, Bus, BedDouble,
  Package, UtensilsCrossed, Calendar, Heart, BookMarked,
  BarChart3, Database, Cpu, UserPlus, Layers, Clock,
  Users2, Compass,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { useAuthStore } from "@/lib/auth";

type NavItem = {
  label: string;
  href: string;
  icon: React.ElementType;
  roles?: string[];
};

const navItems: NavItem[] = [
  // ── Core ──────────────────────────────────────────────────────────────────
  { label: "Dashboard",     href: "/dashboard",               icon: LayoutDashboard },
  { label: "Students",      href: "/dashboard/students",      icon: Users,          roles: ["admin","super_admin","school_admin","registrar","academic_director","teacher"] },
  { label: "Teachers",      href: "/dashboard/teachers",      icon: UserCheck,      roles: ["admin","super_admin","school_admin","hr_manager","academic_director"] },
  { label: "Admissions",    href: "/dashboard/admissions",    icon: UserPlus,       roles: ["admin","super_admin","school_admin","registrar"] },

  // ── Academic ──────────────────────────────────────────────────────────────
  { label: "Attendance",    href: "/dashboard/attendance",    icon: CalendarCheck,  roles: ["admin","super_admin","teacher","academic_director","parent","student"] },
  { label: "Exams",         href: "/dashboard/exams",         icon: BookOpen,       roles: ["admin","super_admin","teacher","academic_director","student","parent"] },
  { label: "CBC",           href: "/dashboard/cbc",           icon: Layers,         roles: ["admin","super_admin","teacher","academic_director"] },
  { label: "LMS",           href: "/dashboard/lms",           icon: Cpu,            roles: ["admin","super_admin","teacher","academic_director","student"] },
  { label: "Timetable",     href: "/dashboard/timetable",     icon: Clock,          roles: ["admin","super_admin","teacher","academic_director","student","parent"] },

  // ── Finance ───────────────────────────────────────────────────────────────
  { label: "Fees",          href: "/dashboard/fees",          icon: DollarSign,     roles: ["admin","super_admin","school_admin","finance_officer","parent","student"] },

  // ── HR ────────────────────────────────────────────────────────────────────
  { label: "HR",            href: "/dashboard/hr",            icon: Briefcase,      roles: ["admin","super_admin","school_admin","hr_manager"] },

  // ── Support Services ──────────────────────────────────────────────────────
  { label: "Library",       href: "/dashboard/library",       icon: BookMarked,     roles: ["admin","super_admin","school_admin","teacher","student"] },
  { label: "Hostel",        href: "/dashboard/hostel",        icon: BedDouble,      roles: ["admin","super_admin","school_admin"] },
  { label: "Transport",     href: "/dashboard/transport",     icon: Bus,            roles: ["admin","super_admin","school_admin","parent","student"] },
  { label: "Health",        href: "/dashboard/health",        icon: Heart,          roles: ["admin","super_admin","school_admin","teacher"] },
  { label: "Cafeteria",     href: "/dashboard/cafeteria",     icon: UtensilsCrossed,roles: ["admin","super_admin","school_admin"] },
  { label: "Inventory",     href: "/dashboard/inventory",     icon: Package,        roles: ["admin","super_admin","school_admin"] },

  // ── Student Life ──────────────────────────────────────────────────────────
  { label: "Discipline",    href: "/dashboard/discipline",    icon: ShieldAlert,    roles: ["admin","super_admin","school_admin","academic_director","teacher"] },
  { label: "Achievements",  href: "/dashboard/achievements",  icon: Award,          roles: ["admin","super_admin","teacher","academic_director","student"] },
  { label: "Scholarships",  href: "/dashboard/scholarships",  icon: Briefcase,      roles: ["admin","super_admin","finance_officer","registrar"] },
  { label: "Events",        href: "/dashboard/events",        icon: Calendar,       roles: ["admin","super_admin","teacher","academic_director","student","parent"] },
  { label: "Mentorship",    href: "/dashboard/mentorship",    icon: Users2,         roles: ["admin","super_admin","teacher","academic_director"] },
  { label: "Alumni",        href: "/dashboard/alumni",        icon: GraduationCap,  roles: ["admin","super_admin","school_admin","registrar"] },
  { label: "DigiGuide",     href: "/dashboard/digiguide",     icon: Compass,        roles: ["admin","super_admin","teacher","academic_director","student"] },

  // ── Communications ────────────────────────────────────────────────────────
  { label: "Notices",       href: "/dashboard/noticeboard",   icon: Bell },
  { label: "Announcements", href: "/dashboard/announcements", icon: MessageSquare,  roles: ["admin","super_admin","school_admin","teacher","academic_director"] },
  { label: "SMS",           href: "/dashboard/sms",           icon: MessageSquare,  roles: ["admin","super_admin","school_admin"] },

  // ── Analytics & Gov ───────────────────────────────────────────────────────
  { label: "Analytics",     href: "/dashboard/analytics",     icon: BarChart3,      roles: ["admin","super_admin","school_admin","academic_director","finance_officer"] },
  { label: "NEMIS",         href: "/dashboard/nemis",         icon: Database,       roles: ["admin","super_admin","school_admin","registrar"] },
  { label: "Facilities",    href: "/dashboard/facilities",    icon: Building2,      roles: ["admin","super_admin","school_admin"] },

  // ── Portals ───────────────────────────────────────────────────────────────
  { label: "My Portal",     href: "/dashboard/teacher",       icon: ClipboardList,  roles: ["teacher"] },
  { label: "My Portal",     href: "/dashboard/student",       icon: GraduationCap,  roles: ["student"] },
  { label: "My Children",   href: "/dashboard/parent",        icon: Users,          roles: ["parent"] },

  // ── Reports & Settings ────────────────────────────────────────────────────
  { label: "Reports",       href: "/dashboard/reports",       icon: FileBarChart,   roles: ["admin","super_admin","school_admin","academic_director","finance_officer"] },
  { label: "Settings",      href: "/dashboard/settings",      icon: Settings,       roles: ["admin","super_admin","school_admin"] },
];

export function Sidebar() {
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);
  const user = useAuthStore((s) => s.user);
  const role = user?.role ?? "student";

  const visibleItems = navItems.filter(
    (item) => !item.roles || item.roles.includes(role)
  );

  const NavContent = () => (
    <nav className="flex flex-col gap-0.5 p-3 overflow-y-auto flex-1">
      {visibleItems.map(({ label, href, icon: Icon }) => {
        const active =
          href === "/dashboard"
            ? pathname === "/dashboard"
            : pathname.startsWith(href);
        return (
          <Link
            key={href + label}
            href={href}
            onClick={() => setMobileOpen(false)}
            className={cn(
              "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
              active
                ? "bg-primary text-primary-foreground"
                : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
            )}
          >
            <Icon className="h-4 w-4 shrink-0" />
            {label}
          </Link>
        );
      })}
    </nav>
  );

  return (
    <>
      {/* Desktop sidebar */}
      <aside className="hidden md:flex flex-col w-60 border-r bg-card min-h-screen">
        <div className="flex items-center gap-2 px-4 py-4 border-b shrink-0">
          <div className="bg-primary rounded-md p-1.5">
            <GraduationCap className="h-5 w-5 text-primary-foreground" />
          </div>
          <span className="font-bold text-sm leading-tight">CBC EMIS Kenya</span>
        </div>
        <NavContent />
      </aside>

      {/* Mobile toggle */}
      <div className="md:hidden fixed top-4 left-4 z-50">
        <Button variant="outline" size="icon" onClick={() => setMobileOpen(!mobileOpen)}>
          {mobileOpen ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
        </Button>
      </div>

      {/* Mobile drawer */}
      {mobileOpen && (
        <div className="md:hidden fixed inset-0 z-40 flex">
          <div className="fixed inset-0 bg-black/40" onClick={() => setMobileOpen(false)} />
          <aside className="relative flex flex-col w-60 bg-card min-h-screen z-50">
            <div className="flex items-center gap-2 px-4 py-4 border-b shrink-0">
              <div className="bg-primary rounded-md p-1.5">
                <GraduationCap className="h-5 w-5 text-primary-foreground" />
              </div>
              <span className="font-bold text-sm">CBC EMIS Kenya</span>
            </div>
            <NavContent />
          </aside>
        </div>
      )}
    </>
  );
}
