// World Animals: tamed animals fight on their owner's side in War Engine.
//
// War Engine marks every player and soldier of faction i with the tag `war_f<i>`, and every soldier with
// `war_h<i>` for each faction i it is hostile to. Tags are shared between packs, so this script copies the owner's
// `war_f<i>` onto each of their tamed animals. The animals' targeting filters (entities/*) then leave alone anyone
// with the same `war_f<i>` and any soldier / war dog without `war_h<i>`, and go after soldiers that do have it.
// Allied soldiers never shoot a pet first (War Engine only fights animals that attack its men), and enemy melee
// soldiers and war dogs see the pet as one of the faction.
//
// The game doesn't tell scripts who owns a tamed animal once the taming component is gone, so the owner is saved
// on the animal (`wa:owner`) when a player tames it, and copied to babies born from tamed parents.
import { world, system } from "@minecraft/server";
import "./falconry.js";
import "./dogs.js";

const NS = "worldanimals:";
const NF = 40;
const OWNER = "wa:owner";
const DIMS = ["overworld", "nether", "the_end"];

const isOurs = (e) => e?.typeId?.startsWith(NS);
const isPet = (e) => { try { return isOurs(e) && e.hasComponent("minecraft:is_tamed"); } catch { return false; } };

function factionOf(p) {
  for (let i = 1; i <= NF; i++) if (p.hasTag(`war_f${i}`)) return i;
  return 0;
}

function setFaction(e, f) {
  for (let i = 1; i <= NF; i++) {
    const want = i === f, has = e.hasTag(`war_f${i}`);
    if (want && !has) e.addTag(`war_f${i}`);
    else if (!want && has) e.removeTag(`war_f${i}`);
  }
}

function sync(e) {
  const id = e.getDynamicProperty(OWNER);
  if (typeof id !== "string") return;
  const owner = world.getEntity(id);              // only while the owner is online; otherwise keep the last faction
  if (owner?.typeId === "minecraft:player") setFaction(e, factionOf(owner));
}

// taming: the tame item is used on the animal; a moment later it is tamed and this player is its owner
world.afterEvents.playerInteractWithEntity.subscribe(({ player, target }) => {
  if (!isOurs(target)) return;
  const wasPet = isPet(target);
  system.runTimeout(() => {
    try {
      if (!target.isValid || !isPet(target)) return;
      // just tamed, or a pet tamed before this script existed (first one to use it claims it)
      if (!wasPet || typeof target.getDynamicProperty(OWNER) !== "string") {
        target.setDynamicProperty(OWNER, player.id);
        sync(target);
      }
    } catch {}
  }, 2);
});

// babies of tamed parents belong to the parents' owner
world.afterEvents.entitySpawn.subscribe(({ entity, cause }) => {
  if (cause !== "Born" || !isOurs(entity)) return;
  system.runTimeout(() => {
    try {
      if (!entity.isValid || !isPet(entity)) return;
      const parents = entity.dimension.getEntities({ type: entity.typeId, location: entity.location, maxDistance: 8 });
      for (const p of parents) {
        const id = p.id !== entity.id && p.getDynamicProperty(OWNER);
        if (typeof id === "string") { entity.setDynamicProperty(OWNER, id); sync(entity); return; }
      }
    } catch {}
  }, 2);
});

// keep every pet's faction tag in step with its owner's (joining / leaving / switching factions)
system.runInterval(() => {
  for (const d of DIMS) {
    let pets = [];
    try { pets = world.getDimension(d).getEntities({ families: ["worldanimals_pet"] }); } catch { continue; }
    for (const e of pets) { try { sync(e); } catch {} }
  }
}, 40);
