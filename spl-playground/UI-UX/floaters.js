const count = 22;
for (let i = 0; i < count; i++) {
  const dot = document.createElement('div');
  dot.className = 'floating-dot';
  dot.style.left = `${Math.random() * 100}%`;
  dot.style.top = `${Math.random() * 100}%`;
  dot.style.width = `${6 + Math.random() * 12}px`;
  dot.style.height = dot.style.width;
  dot.style.animationDelay = `${Math.random() * 8}s`;
  dot.style.animationDuration = `${8 + Math.random() * 8}s`;
  document.body.appendChild(dot);
}
