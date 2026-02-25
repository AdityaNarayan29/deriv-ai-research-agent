"use client";

import { useEffect } from "react";
import gsap from "gsap";

export function useGraphAnimations(nodeCount: number, edgeCount: number) {
  useEffect(() => {
    if (!nodeCount) return;

    // Wait for React Flow to render DOM elements
    const timer = requestAnimationFrame(() => {
      const tl = gsap.timeline();

      // 1. Nodes: staggered scale + fade in
      tl.fromTo(
        ".react-flow__node",
        { opacity: 0, scale: 0 },
        {
          opacity: 1,
          scale: 1,
          duration: 0.4,
          stagger: 0.06,
          ease: "back.out(1.4)",
        }
      );

      // 2. Edges: fade in
      tl.fromTo(
        ".react-flow__edge",
        { opacity: 0 },
        {
          opacity: 1,
          duration: 0.5,
          stagger: 0.04,
          ease: "power2.out",
        },
        "-=0.2"
      );

      // 3. Edge labels: fade in
      tl.fromTo(
        ".react-flow__edgelabel-renderer > div",
        { opacity: 0 },
        {
          opacity: 1,
          duration: 0.3,
          stagger: 0.03,
        },
        "-=0.3"
      );
    });

    return () => cancelAnimationFrame(timer);
  }, [nodeCount, edgeCount]);
}
