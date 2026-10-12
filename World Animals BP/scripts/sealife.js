// Octopus: hurt it and it squirts ink: a cloud of ink, whoever is right next to it is blinded for a moment,
// and it jets away.
import { world, system } from "@minecraft/server";

const OCTOPUS = "worldanimals:octopus";
const lastInk = new Map();

world.afterEvents.entityHurt.subscribe(({ hurtEntity: o, damageSource }) => {
  if (o?.typeId !== OCTOPUS) return;
  const now = system.currentTick;
  if (now - (lastInk.get(o.id) ?? -1e9) < 100) return;
  lastInk.set(o.id, now);
  try {
    const l = o.location, dim = o.dimension;
    for (let i = 0; i < 24; i++) {
      dim.spawnParticle("minecraft:squid_ink_bubble",
        { x: l.x + (Math.random() - 0.5) * 2.4, y: l.y + 0.3 + Math.random() * 1.2, z: l.z + (Math.random() - 0.5) * 2.4 });
    }
    dim.playSound("mob.squid.hurt", l, { pitch: 0.8 });
    for (const e of dim.getEntities({ location: l, maxDistance: 4 })) {
      if (e.id === o.id) continue;
      try { e.addEffect("blindness", 60, { amplifier: 0, showParticles: false }); } catch {}
    }
    const a = damageSource?.damagingEntity;
    if (a) {
      const dx = l.x - a.location.x, dz = l.z - a.location.z, L = Math.hypot(dx, dz) || 1;
      o.applyImpulse({ x: (dx / L) * 1.2, y: 0.25, z: (dz / L) * 1.2 });
    }
  } catch {}
});
