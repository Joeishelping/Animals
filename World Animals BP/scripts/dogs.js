// Dog jobs (tamed dogs only; the guard breeds' fighting is in their behaviour files):
//   every dog     barks when a monster or an enemy soldier comes within 16 blocks, and tells its owner what and where
//   Border Collie herds: while its owner sneaks nearby, livestock around the collie is driven towards the owner
//   retrievers    (Golden Retriever, Labrador, Beagle) fetch the drops of anything their owner kills near them
import { world, system } from "@minecraft/server";

const NS = "worldanimals:";
const OWNER = "wa:owner";
const NF = 40;
const DIMS = ["overworld", "nether", "the_end"];
const RETRIEVERS = new Set([NS + "golden_retriever", NS + "labrador", NS + "beagle"]);
const COLLIE = NS + "border_collie";
const LIVESTOCK = ["sheep", "cow", "pig", "chicken", "goat", "llama", "horse", "wa_grazers", "zebra", "buffalo",
  "american_bison", "przewalski_horse", "turkey", "duck"];

const lastBark = new Map();
const ownerOf = (d) => { try { const id = d.getDynamicProperty(OWNER); return typeof id === "string" ? world.getEntity(id) : undefined; } catch { return undefined; } };
const fam = (e, f) => { try { return !!e.getComponent("minecraft:type_family")?.hasTypeFamily(f); } catch { return false; } };
const sitting = (e) => { try { return e.hasComponent("minecraft:is_sitting") || !!e.getComponent("minecraft:sittable")?.isSitting; } catch { return false; } };
const factionOf = (p) => { for (let i = 1; i <= NF; i++) if (p.hasTag(`war_f${i}`)) return i; return 0; };
const name = (e) => e.typeId.split(":")[1].replace(/_/g, " ");

function bearing(from, to) {
  const deg = (Math.atan2(to.x - from.x, -(to.z - from.z)) * 180 / Math.PI + 360) % 360;
  return ["N", "NE", "E", "SE", "S", "SW", "W", "NW"][Math.round(deg / 45) % 8];
}

function threat(owner, e) {
  const f = factionOf(owner);
  if (e.hasTag(f ? `war_f${f}` : "__none__")) return false;
  if (fam(e, "monster") && !fam(e, "worldanimals_pet")) return true;
  if (f && (fam(e, "war_soldier") || fam(e, "war_hound")) && e.hasTag(`war_h${f}`)) return true;
  return false;
}

function tamedDogs() {
  const out = [];
  for (const d of DIMS) {
    try { out.push(...world.getDimension(d).getEntities({ families: ["wa_dogs", "worldanimals_pet"] })); } catch {}
  }
  return out;
}

// alarm
system.runInterval(() => {
  const now = system.currentTick;
  for (const dog of tamedDogs()) {
    try {
      if (now - (lastBark.get(dog.id) ?? -1e9) < 200) continue;
      const owner = ownerOf(dog);
      if (!owner || owner.dimension.id !== dog.dimension.id) continue;
      const near = dog.dimension.getEntities({ location: dog.location, maxDistance: 16 }).filter((e) => threat(owner, e));
      if (!near.length) continue;
      lastBark.set(dog.id, now);
      dog.dimension.playSound("mob.wolf.bark", dog.location, { volume: 1.2 });
      const first = near.sort((a, b) => a.location.y - b.location.y)[0];
      const what = near.length > 1 ? `${near.length} threats` : name(first);
      const d = Math.round(Math.hypot(first.location.x - owner.location.x, first.location.z - owner.location.z));
      if (d < 64) owner.onScreenDisplay.setActionBar(`§6Your ${name(dog)} is barking: §c${what} ${bearing(owner.location, first.location)} ${d}m`);
    } catch {}
  }
}, 40);

// herding
system.runInterval(() => {
  for (const d of DIMS) {
    let collies = [];
    try { collies = world.getDimension(d).getEntities({ type: COLLIE, families: ["worldanimals_pet"] }); } catch { continue; }
    for (const c of collies) {
      try {
        const owner = ownerOf(c);
        if (!owner?.isSneaking || owner.dimension.id !== d || sitting(c)) continue;
        const o = owner.location;
        if (Math.hypot(o.x - c.location.x, o.z - c.location.z) > 32) continue;
        for (const a of c.dimension.getEntities({ location: c.location, maxDistance: 14 })) {
          if (!LIVESTOCK.some((f) => fam(a, f)) || fam(a, "worldanimals_pet")) continue;
          const dx = o.x - a.location.x, dz = o.z - a.location.z, L = Math.hypot(dx, dz);
          if (L < 4) continue;
          a.applyImpulse({ x: (dx / L) * 0.12, y: 0, z: (dz / L) * 0.12 });
        }
      } catch {}
    }
  }
}, 10);

// retrieving
world.afterEvents.entityDie.subscribe(({ deadEntity, damageSource }) => {
  const killer = damageSource?.damagingEntity;
  if (killer?.typeId !== "minecraft:player") return;
  let at, dim;
  try { at = { ...deadEntity.location }; dim = deadEntity.dimension; } catch { return; }
  let dog;
  try {
    dog = dim.getEntities({ location: at, maxDistance: 24, families: ["wa_dogs", "worldanimals_pet"] })
      .find((d) => RETRIEVERS.has(d.typeId) && ownerOf(d)?.id === killer.id && !sitting(d));
  } catch {}
  if (!dog) return;
  system.runTimeout(() => {
    try {
      const items = dim.getEntities({ type: "minecraft:item", location: at, maxDistance: 3 });
      if (!items.length) return;
      dog.teleport(at);
      system.runTimeout(() => {
        try {
          for (const it of items) if (it.isValid) it.teleport(killer.location);
          dim.playSound("random.pop", killer.location);
          killer.onScreenDisplay.setActionBar(`§6Your ${name(dog)} fetched it`);
        } catch {}
      }, 20);
    } catch {}
  }, 10);
});
