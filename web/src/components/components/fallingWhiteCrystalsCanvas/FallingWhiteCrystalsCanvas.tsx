"use client";
import React, { useEffect, useRef } from "react";

const FallingWhiteCrystalsCanvas = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext("2d");
    if (!ctx || !canvas) return;

    const particles = [] as any;
    const maxParticles = 100;
    const width = window.innerWidth;
    const height = window.innerHeight;

    const resizeCanvas = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };

    resizeCanvas();
    window.addEventListener("resize", resizeCanvas);

    const createParticle = () => {
      const size = Math.random() * 5 + 2;
      const speed = Math.random() * 2 + 0.5;
      return {
        x: Math.random() * width,
        y: Math.random() * height,
        size,
        speed,
        velY: Math.random() * speed,
        velX: Math.random() * 2 - 1,
      };
    };

    const updateParticles = () => {
      ctx.clearRect(0, 0, width, height);
      particles.forEach((particle: any, i: number) => {
        particle.y += particle.velY;
        particle.x += particle.velX;

        if (particle.y > height) {
          particles[i] = createParticle();
          particles[i].y = 0;
        }

        if (particle.x > width || particle.x < 0) {
          particles[i] = createParticle();
        }

        ctx.beginPath();
        ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
        ctx.fillStyle = "rgba(255, 255, 255, 0.8)";
        ctx.fill();
      });
      requestAnimationFrame(updateParticles);
    };

    for (let i = 0; i < maxParticles; i++) {
      particles.push(createParticle());
    }

    updateParticles();

    return () => {
      window.removeEventListener("resize", resizeCanvas);
    };
  }, []);

  return (
    <div
      style={{
        paddingTop: "4.2rem",
        position: "absolute",
        top: 0,
        left: 0,
        width: "100vw",
        height: "100vh",
        overflow: "hidden",
        pointerEvents: "none",
        zIndex: -1,
      }}
    >
      <canvas
        ref={canvasRef}
        style={{
          width: "100%",
          height: "100%",
          backgroundColor: "transparent",
          pointerEvents: "none",
        }}
      ></canvas>
    </div>
  );
};

export default FallingWhiteCrystalsCanvas;
