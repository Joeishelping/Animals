// Falconry: a tamed Saker Falcon works from its owner's arm with the Falconry Glove.
//
//   right-click your falcon holding the glove    it hops onto your arm
//   use the glove looking at a mob               strike: it dives on it (small prey dies, the drops come back to you)
//   use the glove looking at open sky            scout: it circles high above for 30 s and reports what it sees
//   sneak + use the glove                        recall it (or, when it's on your arm, let it fly free)
//
// Flight is driven from here (teleports every tick, so it is smooth and goes where it is sent). The falcon sits on
// the player's own arm seat, the one parrots use, so it moves with you.
import { world, system, EntityDamageCause, EquipmentSlot } from "@minecraft/server";

const FALCON = "worldanimals:saker_falcon";
const GLOVE = "worldanimals:falconry_glove";
const OWNER = "wa:owner";
const NF = 40;
const SMALL_PREY = ["rabbit", "chicken", "rat", "squirrel", "duck", "dove", "turkey", "parrot", "frog", "kiwi",
  "cyanocitta_cristata", "tucan", "raccoon", "skunk", "opossum", "erizo", "fish"];
const STRIKE_SPEED = 1.15, RETURN_SPEED = 0.8, SCOUT_TICKS = 600;

const flights = new Map();   // falcon id -> { mode: "strike" | "return" | "scout", owner, target?, t, angle?, home? }

const held = (p) => { try { return p.getComponent("minecraft:equippable")?.getEquipment(EquipmentSlot.Mainhand)?.typeId; } catch { return undefined; } };
const ownerId = (f) => { try { return f.getDynamicProperty(OWNER); } catch { return undefined; } };
const isTamed = (f) => { try { return f.hasComponent("minecraft:is_tamed"); } catch { return false; } };
const ridingOn = (e) => { try { return e.getComponent("minecraft:riding")?.entityRidingOn; } catch { return undefined; } };
const dist = (a, b) => Math.hypot(a.x - b.x, a.y - b.y, a.z - b.z);
const say = (p, msg) => { try { p.onScreenDisplay.setActionBar(msg); } catch {} };

function factionOf(p) { for (let i = 1; i <= NF; i++) if (p.hasTag(`war_f${i}`)) return i; return 0; }
function hasFamily(e, fam) { try { return !!e.getComponent("minecraft:type_family")?.hasTypeFamily(fam); } catch { return false; } }

// someone the owner's falcon must never hit
function isFriend(owner, e) {
  if (e.id === owner.id) return true;
  if (ownerId(e) === owner.id) return true;                         // your own animals
  const f = factionOf(owner);
  if (!f) return false;
  if (e.hasTag(`war_f${f}`)) return true;                           // your faction (players, soldiers, pets)
  if ((hasFamily(e, "war_soldier") || hasFamily(e, "war_hound")) && !e.hasTag(`war_h${f}`)) return true;   // allied / neutral army
  return false;
}
// someone the falcon reports when scouting
function isThreat(owner, e) {
  if (isFriend(owner, e)) return false;
  if (hasFamily(e, "monster")) return true;
  const f = factionOf(owner);
  if (f && (hasFamily(e, "war_soldier") || hasFamily(e, "war_hound")) && e.hasTag(`war_h${f}`)) return true;
  if (f && e.typeId === "minecraft:player" && factionOf(e) && factionOf(e) !== f) return true;
  return false;
}

function myFalcons(p, range = 64) {
  try {
    return p.dimension.getEntities({ type: FALCON, location: p.location, maxDistance: range })
      .filter((f) => isTamed(f) && ownerId(f) === p.id);
  } catch { return []; }
}
const perchedFalcon = (p) => myFalcons(p, 4).find((f) => ridingOn(f)?.id === p.id);

function perch(p, f) {
  flights.delete(f.id);
  try {
    if (!p.getComponent("minecraft:rideable")?.addRider(f)) {
      f.teleport({ x: p.location.x, y: p.location.y + 1.6, z: p.location.z });
      system.runTimeout(() => { try { p.getComponent("minecraft:rideable")?.addRider(f); } catch {} }, 2);
    }
    p.dimension.playSound("mob.eagle.idle", p.location, { volume: 0.6, pitch: 1.4 });
  } catch {}
}
function launch(p, f) {
  try { p.getComponent("minecraft:rideable")?.ejectRider(f); } catch {}
  try { f.teleport({ x: p.location.x, y: p.location.y + 2.0, z: p.location.z }); } catch {}
}

function bearing(from, to) {
  const deg = (Math.atan2(to.x - from.x, -(to.z - from.z)) * 180 / Math.PI + 360) % 360;
  return ["N", "NE", "E", "SE", "S", "SW", "W", "NW"][Math.round(deg / 45) % 8];
}

// ---------------------------------------------------------------- commands
world.beforeEvents.playerInteractWithEntity.subscribe((ev) => {
  const { player, target } = ev;
  if (target?.typeId !== FALCON || held(player) !== GLOVE) return;
  if (!isTamed(target) || ownerId(target) !== player.id) return;
  ev.cancel = true;                                                  // no sit toggle: it comes to the glove
  system.run(() => { try { perch(player, target); say(player, "§6Falcon on the glove"); } catch {} });
});

world.afterEvents.itemUse.subscribe(({ source: p, itemStack }) => {
  if (itemStack?.typeId !== GLOVE || p.typeId !== "minecraft:player") return;
  const onArm = perchedFalcon(p);
  const out = myFalcons(p).find((f) => flights.has(f.id) || ridingOn(f)?.id !== p.id);
  if (p.isSneaking) {
    if (onArm) { launch(p, onArm); say(p, "§7Falcon released"); return; }
    if (out) { flights.set(out.id, { mode: "return", owner: p.id, t: 0 }); say(p, "§6Falcon recalled"); return; }
    say(p, "§7No falcon nearby"); return;
  }
  if (!onArm) {
    if (out) { flights.set(out.id, { mode: "return", owner: p.id, t: 0 }); say(p, "§6Falcon coming back to the glove"); }
    else say(p, "§7Right-click your falcon with the glove to put it on your arm");
    return;
  }
  let hit;
  try { hit = p.getEntitiesFromViewDirection({ maxDistance: 48 }).map((h) => h.entity).find((e) => e.id !== onArm.id && e.typeId !== "minecraft:item"); } catch {}
  if (hit) {
    if (isFriend(p, hit)) { say(p, "§cYour falcon won't strike a friend"); return; }
    launch(p, onArm);
    flights.set(onArm.id, { mode: "strike", owner: p.id, target: hit.id, t: 0 });
    p.dimension.playSound("mob.eagle.idle", p.location, { volume: 1.0, pitch: 0.8 });
    say(p, "§6Strike!");
  } else {
    launch(p, onArm);
    flights.set(onArm.id, { mode: "scout", owner: p.id, t: 0, angle: 0 });
    say(p, "§6Falcon scouting...");
  }
});

// ---------------------------------------------------------------- flight
function step(f, to, speed, face) {
  const l = f.location, d = dist(l, to);
  const k = d > speed ? speed / d : 1;
  const next = { x: l.x + (to.x - l.x) * k, y: l.y + (to.y - l.y) * k, z: l.z + (to.z - l.z) * k };
  f.teleport(next, { facingLocation: face ?? to });
  return d;
}

function strike(f, fl, owner) {
  const t = world.getEntity(fl.target);
  if (!t?.isValid || t.dimension.id !== f.dimension.id || fl.t > 160) { fl.mode = "return"; fl.t = 0; return; }
  const aim = { x: t.location.x, y: t.location.y + 0.6, z: t.location.z };
  if (step(f, aim, STRIKE_SPEED) < 1.4) {
    const small = SMALL_PREY.some((fam) => hasFamily(t, fam));
    const at = { ...t.location };
    try { t.applyDamage(small ? 40 : 6, { cause: EntityDamageCause.entityAttack, damagingEntity: f }); } catch {}
    try { f.dimension.spawnParticle("minecraft:critical_hit_emitter", aim); } catch {}
    try { f.dimension.playSound("mob.eagle.hurt", aim, { pitch: 1.3 }); } catch {}
    // the catch comes back to the falconer
    system.runTimeout(() => {
      try {
        const o = world.getEntity(fl.owner);
        if (!o) return;
        for (const it of f.dimension.getEntities({ type: "minecraft:item", location: at, maxDistance: 3 }))
          it.teleport(o.location);
      } catch {}
    }, 15);
    fl.mode = "return"; fl.t = 0;
  }
}

function scout(f, fl, owner) {
  if (fl.t > SCOUT_TICKS) { fl.mode = "return"; fl.t = 0; return; }
  fl.angle += 0.06;
  const c = owner.location;
  const r = 12;
  const at = { x: c.x + Math.cos(fl.angle) * r, y: c.y + 20, z: c.z + Math.sin(fl.angle) * r };
  const ahead = { x: c.x + Math.cos(fl.angle + 0.3) * r, y: c.y + 20, z: c.z + Math.sin(fl.angle + 0.3) * r };
  step(f, at, 1.0, ahead);
  if (fl.t % 40 === 0) {
    let seen = [];
    try { seen = owner.dimension.getEntities({ location: c, maxDistance: 64 }).filter((e) => isThreat(owner, e)); } catch {}
    const groups = new Map();
    for (const e of seen) {
      const name = e.typeId === "minecraft:player" ? "enemy player" : hasFamily(e, "war_soldier") ? "enemy soldier"
        : e.typeId.split(":")[1].replace(/_/g, " ");
      const key = `${name}|${bearing(c, e.location)}`;
      const g = groups.get(key) ?? { name, dir: bearing(c, e.location), n: 0, d: 1e9 };
      g.n++; g.d = Math.min(g.d, Math.round(dist(c, e.location)));
      groups.set(key, g);
      try { e.dimension.spawnParticle("minecraft:villager_angry", { x: e.location.x, y: e.location.y + 2.4, z: e.location.z }); } catch {}
    }
    const msg = [...groups.values()].sort((a, b) => a.d - b.d).slice(0, 4)
      .map((g) => `${g.n} ${g.name}${g.n > 1 ? "s" : ""} ${g.dir} ${g.d}m`).join("§7, §c");
    say(owner, seen.length ? `§6Falcon sees: §c${msg}` : "§6Falcon sees: §anothing hostile");
  }
}

system.runInterval(() => {
  for (const [id, fl] of [...flights]) {
    try {
      const f = world.getEntity(id);
      const owner = world.getEntity(fl.owner);
      if (!f?.isValid || !owner?.isValid || f.dimension.id !== owner.dimension.id) { flights.delete(id); continue; }
      fl.t++;
      if (fl.mode === "strike") strike(f, fl, owner);
      else if (fl.mode === "scout") scout(f, fl, owner);
      else if (fl.mode === "return") {
        const arm = { x: owner.location.x, y: owner.location.y + 1.7, z: owner.location.z };
        if (step(f, arm, RETURN_SPEED) < 1.6 || fl.t > 400) {
          if (held(owner) === GLOVE || dist(f.location, owner.location) < 3) perch(owner, f);
          flights.delete(id);
        }
      }
    } catch { flights.delete(id); }
  }
}, 1);
