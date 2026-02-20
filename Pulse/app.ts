// Avila Pulse - Advanced Animations Engine
// TypeScript Configuration

interface Particle {
    x: number;
    y: number;
    vx: number;
    vy: number;
    size: number;
    color: string;
    alpha: number;
}

interface MousePosition {
    x: number;
    y: number;
}

class PulseAnimationEngine {
    private canvas: HTMLCanvasElement;
    private ctx: CanvasRenderingContext2D;
    private particles: Particle[] = [];
    private mouse: MousePosition = { x: 0, y: 0 };
    private particleCount: number = 100;
    private connectionDistance: number = 150;

    constructor(canvasId: string) {
        this.canvas = document.getElementById(canvasId) as HTMLCanvasElement;
        this.ctx = this.canvas.getContext('2d')!;
        this.init();
    }

    private init(): void {
        this.resize();
        this.createParticles();
        this.animate();
        this.setupEventListeners();
    }

    private resize(): void {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    }

    private createParticles(): void {
        const colors = ['#007AFF', '#5856D6', '#FF2D55', '#FFD60A'];

        for (let i = 0; i < this.particleCount; i++) {
            this.particles.push({
                x: Math.random() * this.canvas.width,
                y: Math.random() * this.canvas.height,
                vx: (Math.random() - 0.5) * 1,
                vy: (Math.random() - 0.5) * 1,
                size: Math.random() * 3 + 1,
                color: colors[Math.floor(Math.random() * colors.length)],
                alpha: Math.random() * 0.5 + 0.3
            });
        }
    }

    private drawParticle(particle: Particle): void {
        this.ctx.beginPath();
        this.ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
        this.ctx.fillStyle = particle.color;
        this.ctx.globalAlpha = particle.alpha;
        this.ctx.fill();
        this.ctx.globalAlpha = 1;
    }

    private connectParticles(): void {
        for (let i = 0; i < this.particles.length; i++) {
            for (let j = i + 1; j < this.particles.length; j++) {
                const dx = this.particles[i].x - this.particles[j].x;
                const dy = this.particles[i].y - this.particles[j].y;
                const distance = Math.sqrt(dx * dx + dy * dy);

                if (distance < this.connectionDistance) {
                    this.ctx.beginPath();
                    this.ctx.moveTo(this.particles[i].x, this.particles[i].y);
                    this.ctx.lineTo(this.particles[j].x, this.particles[j].y);
                    this.ctx.strokeStyle = this.particles[i].color;
                    this.ctx.globalAlpha = (1 - distance / this.connectionDistance) * 0.2;
                    this.ctx.lineWidth = 1;
                    this.ctx.stroke();
                    this.ctx.globalAlpha = 1;
                }
            }
        }
    }

    private updateParticles(): void {
        this.particles.forEach(particle => {
            particle.x += particle.vx;
            particle.y += particle.vy;

            // Mouse attraction
            const dx = this.mouse.x - particle.x;
            const dy = this.mouse.y - particle.y;
            const distance = Math.sqrt(dx * dx + dy * dy);

            if (distance < 200) {
                const force = (200 - distance) / 200;
                particle.vx += dx * force * 0.001;
                particle.vy += dy * force * 0.001;
            }

            // Boundaries
            if (particle.x < 0 || particle.x > this.canvas.width) particle.vx *= -1;
            if (particle.y < 0 || particle.y > this.canvas.height) particle.vy *= -1;

            // Velocity limits
            const maxVelocity = 2;
            particle.vx = Math.max(-maxVelocity, Math.min(maxVelocity, particle.vx));
            particle.vy = Math.max(-maxVelocity, Math.min(maxVelocity, particle.vy));

            // Friction
            particle.vx *= 0.99;
            particle.vy *= 0.99;
        });
    }

    private animate = (): void => {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        this.updateParticles();
        this.connectParticles();

        this.particles.forEach(particle => {
            this.drawParticle(particle);
        });

        requestAnimationFrame(this.animate);
    }

    private setupEventListeners(): void {
        window.addEventListener('resize', () => this.resize());

        window.addEventListener('mousemove', (e: MouseEvent) => {
            this.mouse.x = e.clientX;
            this.mouse.y = e.clientY;
        });
    }
}

// Text animations
class TextAnimator {
    static typeWriter(element: HTMLElement, text: string, speed: number = 50): void {
        let i = 0;
        element.textContent = '';

        const type = () => {
            if (i < text.length) {
                element.textContent += text.charAt(i);
                i++;
                setTimeout(type, speed);
            }
        };

        type();
    }

    static glitchEffect(element: HTMLElement): void {
        const originalText = element.textContent || '';
        const glitchChars = '!@#$%^&*()_+-=[]{}|;:,.<>?';
        let iterations = 0;
        const maxIterations = 20;

        const glitch = setInterval(() => {
            element.textContent = originalText
                .split('')
                .map((char, index) => {
                    if (index < iterations) {
                        return originalText[index];
                    }
                    return glitchChars[Math.floor(Math.random() * glitchChars.length)];
                })
                .join('');

            if (iterations >= originalText.length) {
                clearInterval(glitch);
                element.textContent = originalText;
            }

            iterations += 1 / 3;
        }, 30);
    }
}

// Scroll effects
class ScrollEffects {
    private elements: NodeListOf<Element>;

    constructor(selector: string) {
        this.elements = document.querySelectorAll(selector);
        this.init();
    }

    private init(): void {
        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('visible');

                        // Add stagger effect
                        const delay = Array.from(this.elements).indexOf(entry.target) * 100;
                        (entry.target as HTMLElement).style.transitionDelay = `${delay}ms`;
                    }
                });
            },
            {
                threshold: 0.1,
                rootMargin: '0px 0px -100px 0px'
            }
        );

        this.elements.forEach((el) => observer.observe(el));
    }
}

// Cursor trail effect
class CursorTrail {
    private trails: Array<{ x: number; y: number; alpha: number }> = [];
    private maxTrails: number = 20;

    constructor() {
        this.init();
    }

    private init(): void {
        document.addEventListener('mousemove', (e: MouseEvent) => {
            this.trails.push({ x: e.clientX, y: e.clientY, alpha: 1 });

            if (this.trails.length > this.maxTrails) {
                this.trails.shift();
            }

            this.updateTrails();
        });
    }

    private updateTrails(): void {
        const existingTrails = document.querySelectorAll('.cursor-trail');
        existingTrails.forEach(trail => trail.remove());

        this.trails.forEach((trail, index) => {
            const trailElement = document.createElement('div');
            trailElement.className = 'cursor-trail';
            trailElement.style.left = `${trail.x}px`;
            trailElement.style.top = `${trail.y}px`;
            trailElement.style.opacity = `${(index / this.maxTrails) * 0.5}`;
            trailElement.style.transform = `scale(${index / this.maxTrails})`;
            document.body.appendChild(trailElement);

            setTimeout(() => trailElement.remove(), 500);
        });
    }
}

// Stats counter animation
class StatsCounter {
    static animateValue(element: HTMLElement, start: number, end: number, duration: number, suffix: string = ''): void {
        const range = end - start;
        const increment = range / (duration / 16);
        let current = start;

        const timer = setInterval(() => {
            current += increment;

            if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
                current = end;
                clearInterval(timer);
            }

            if (suffix === '%') {
                element.textContent = current.toFixed(2) + suffix;
            } else if (suffix === 'ms') {
                element.textContent = current.toFixed(1) + suffix;
            } else if (end > 1000000) {
                element.textContent = (current / 1000000).toFixed(1) + 'M+';
            } else if (end > 1000) {
                element.textContent = (current / 1000).toFixed(0) + 'K+';
            } else {
                element.textContent = Math.floor(current).toLocaleString() + suffix;
            }
        }, 16);
    }
}

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', () => {
    // Initialize particle system
    new PulseAnimationEngine('particles-canvas');

    // Initialize scroll effects
    new ScrollEffects('.animate-on-scroll');

    // Initialize cursor trail
    new CursorTrail();

    // Glitch effect on hero title
    const heroTitle = document.querySelector('.hero h1') as HTMLElement;
    if (heroTitle) {
        setTimeout(() => TextAnimator.glitchEffect(heroTitle), 500);
    }

    // Smooth scroll
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href')!);
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });

    // Parallax effect
    window.addEventListener('scroll', () => {
        const scrolled = window.pageYOffset;
        const parallaxElements = document.querySelectorAll('.parallax');

        parallaxElements.forEach((el) => {
            const speed = parseFloat((el as HTMLElement).dataset.speed || '0.5');
            (el as HTMLElement).style.transform = `translateY(${scrolled * speed}px)`;
        });
    });

    // Stat counters
    const statsObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const statElements = entry.target.querySelectorAll('.stat-number');
                statElements.forEach((stat) => {
                    const target = (stat as HTMLElement).dataset.target;
                    const suffix = (stat as HTMLElement).dataset.suffix || '';
                    if (target) {
                        StatsCounter.animateValue(stat as HTMLElement, 0, parseFloat(target), 2000, suffix);
                    }
                });
                statsObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });

    const statsSection = document.querySelector('.stats-section');
    if (statsSection) {
        statsObserver.observe(statsSection);
    }
});

// Export for use in HTML
export { PulseAnimationEngine, TextAnimator, ScrollEffects, CursorTrail, StatsCounter };
