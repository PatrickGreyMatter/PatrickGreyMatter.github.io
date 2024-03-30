// Function to get particle quantity based on screen width
function getParticleQuantity() {
    return window.innerWidth > 768 ? 80 : 40;
  }
  
  // Load tsParticles with initial options
  function loadParticles() {
    tsParticles.load("tsparticles", {
      background: {
        color: "#000",
      },
      interactivity: {
        events: {
          onClick: {
            enable: true,
            mode: "push",
          },
          onHover: {
            enable: true,
            mode: "repulse",
          },
        },
        modes: {
          push: {
            quantity: 6,
          },
          repulse: {
            distance: 100,
          },
        },
      },
      particles: {
        number: {
          value: getParticleQuantity(),
        },
        links: {
          enable: true,
          opacity: 0.3,
          distance: 200,
        },
        move: {
          enable: true,
          speed: { min: 1, max: 3 },
        },
        opacity: {
          value: { min: 0.3, max: 0.7 },
        },
        size: {
          value: { min: 1, max: 3 },
        },
      },
    });
  }
  
  // Initialize tsParticles
  loadParticles();
  
  // Adjust tsParticles on window resize
  window.addEventListener('resize', loadParticles);
  