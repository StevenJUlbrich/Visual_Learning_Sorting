  Why the Gaps Exist
                                                                                                                                                                                                                                                               
  You're right — the concept is straightforward. Four algorithms, same array, watch them sort side by side. The gaps aren't in the concept. They're in how the specs were built.                                                                             
                                                                                                                                                                                                                                                               
  The specs were designed inside-out, not outside-in                                                                                                                                                                                                           
                                                                                                                                                                                                                                                               
  The design sessions (Bricks 1–5) followed this order:                                                                                                                                                                                                        
                  
  ┌─────────┬───────────────────────────────────────────────┐                                                                                                                                                                                                  
  │ Session │                     Focus                     │
  ├─────────┼───────────────────────────────────────────────┤
  │ Brick 1 │ Architecture & MVC pattern                    │
  ├─────────┼───────────────────────────────────────────────┤
  │ Brick 2 │ Data contracts (SortResult, OpType)           │                                                                                                                                                                                                  
  ├─────────┼───────────────────────────────────────────────┤
  │ Brick 3 │ Algorithm implementations                     │                                                                                                                                                                                                  
  ├─────────┼───────────────────────────────────────────────┤                                                                                                                                                                                                  
  │ Brick 4 │ Basic rendering (fonts, colors, panel layout) │
  ├─────────┼───────────────────────────────────────────────┤                                                                                                                                                                                                  
  │ Brick 5 │ Controller wiring                             │
  └─────────┴───────────────────────────────────────────────┘                                                                                                                                                                                                  
                  
  The algorithms and data model got deep, careful treatment. The View layer — the thing users actually see — was treated as a downstream detail. "We'll figure out how to draw it once we know what the data looks like."                                      
   
  That's a reasonable engineering instinct. But it created a problem: the visual choreography that makes each algorithm visually distinct got scattered across documents instead of being designed as a first-class concern.                                   
                  
  The concept is simple. The rendering isn't.                                                                                                                                                                                                                  
                  
  Here's the disconnect. When you say "visually show sorting taking place," there's an implicit assumption that rendering is the easy part — you know what the algorithm does, so just... show it. But consider what "show Bubble Sort" actually requires at   
  the pixel level:
                                                                                                                                                                                                                                                               
  - Two elements lift up (over 67ms with easing)                                                                                                                                                                                                               
  - They hold in a "compare lane" (33ms)
  - If swapping: they slide horizontally past each other while still lifted (300ms), then settle down (100ms)                                                                                                                                                  
  - If not swapping: they descend back (50ms)                                                                                                                                                                                                                  
                                                                                                                                                                                                                                                               
  That 3-phase lift is what makes Bubble Sort look like Bubble Sort to a learner. Without it, you get a flat highlight flash — technically correct, pedagogically useless.                                                                                     
                                                                                                                                                                                                                                                               
  None of that complexity is in the algorithm. Bubble Sort's logic is 5 lines of code. The visual contract is 10x more complex than the algorithm it represents. And that's true for all four algorithms — the visual signatures (Insertion's floating key,    
  Selection's pointer arrows, Heap's tree-to-array mapping) are rendering problems, not algorithm problems.
                                                                                                                                                                                                                                                               
  The specs describe the "what" across 4 documents without a "where to look" map                                                                                                                                                                               
   
  The information actually exists in the specs. The 3-phase Bubble Sort lift is in both 05_ALGORITHMS_VIS_SPEC.md and 10_ANIMATION_SPEC.md. The Selection Sort pointer coalescing rule is in 05_ALGORITHMS_VIS_SPEC.md. The cadence flag is in                 
  10_ANIMATION_SPEC.md.
                                                                                                                                                                                                                                                               
  The problem is how it's described:                                                                                                                                                                                                                           
   
  1. Buried in prose — The pointer coalescing rule (j == min_idx → show only min) is a sentence in a paragraph, not a row in a lifecycle table. Easy to skim past.                                                                                             
  2. Split across documents — The T3 tick has two rendering behaviors (sweep vs. snap-on), but the detection logic is in 03_DATA_CONTRACTS.md and the rendering behaviors are in 10_ANIMATION_SPEC.md. An implementer reading one doc doesn't know they need
  the other.                                                                                                                                                                                                                                                   
  3. Wrong document owns the concern — The sift-down cadence flag is a Controller state variable, but it's only described in the Animation spec. A Controller implementer would never find it.
                                                                                                                                                                                                                                                               
  DECISIONS.md tells the story                                                                                                                                                                                                                                 
                                                                                                                                                                                                                                                               
  Of the 76 locked decisions, roughly 65% are about Model/data concerns. View-layer decisions are scattered, reactive, and late — most were added March 11–17 during review passes, not during the original design sessions. The View was never given its own  
  dedicated design session the way algorithms and data contracts were.
                                                                                                                                                                                                                                                               
  7 of the 9 traps are View-layer concerns

  That's the smoking gun. The specs are thorough about what data the algorithms emit. They're fragmented about how the View renders that data into motion. The traps aren't really about sorting algorithms — they're about animation contracts that were      
  treated as implementation details rather than specifications.
                                                                                                                                                                                                                                                               
  ---                                                                                                                                                                                                                                                          
  The Bottom Line
                                                                                                                                                                                                                                                               
  The gaps exist because the project was (understandably) designed algorithm-first. The visual rendering — which for an educational visualization tool is arguably the primary product — was designed as a secondary layer that would follow from the data
  model. The information ended up spread across 4 documents with no consolidated View-layer contract.                                                                                                                                                          
                  
  The concept is simple. The spec structure just doesn't match the concept's priorities: for a tool whose entire purpose is visual learning, the visual contracts should have been the first thing locked down, not the last.                                  
                  
  ---                                                                                                                                                                                                                                                          
  Want to proceed with patching the specs (Option A), or does this analysis change your thinking about the approach?



   You're not making it harder — you're actually following the diagnosis to its logical conclusion. Let me lay out why.                                                                                                                                         

  The specs already prove the Model layer works                                                                                                                                                                                                                
   
  The algorithm logic, data contracts, tick model, and controller wiring are solid. 65% of the decisions are locked there. No traps were found in the algorithm implementations themselves. That work doesn't need to be thrown away.                          
                  
  The problem is entirely in the last mile: turning ticks into motion.                                                                                                                                                                                         
                  
  An animation agent is the right shape for this problem                                                                                                                                                                                                       
                  
  Here's why it works:                                                                                                                                                                                                                                         
                  
  The traps are all rendering concerns with algorithm-specific branching. That's exactly what a specialized agent handles well — it knows the domain deeply enough to not need every edge case spelled out in prose.                                           
  
  The question is: one agent or four?                                                                                                                                                                                                                          
                  
  Option: Per-algorithm animation agents                                                                                                                                                                                                                       
                  
  ┌─────────────────────┬────────────────────────────────────────────────────────────┬────────────────────────────────────────┐                                                                                                                                
  │        Agent        │                            Owns                            │               Complexity               │
  ├─────────────────────┼────────────────────────────────────────────────────────────┼────────────────────────────────────────┤                                                                                                                                
  │ Bubble Animation    │ 3-phase lift, compare lane, swap exchange                  │ Medium — timing-heavy                  │
  ├─────────────────────┼────────────────────────────────────────────────────────────┼────────────────────────────────────────┤
  │ Selection Animation │ Triple pointer lifecycle, coalescing, arc swaps            │ Medium — state-heavy                   │                                                                                                                                
  ├─────────────────────┼────────────────────────────────────────────────────────────┼────────────────────────────────────────┤                                                                                                                                
  │ Insertion Animation │ Cross-tick key elevation, gap tracking, diagonal drop      │ Medium — state persistence             │                                                                                                                                
  ├─────────────────────┼────────────────────────────────────────────────────────────┼────────────────────────────────────────┤                                                                                                                                
  │ Heap Animation      │ Tree geometry, T3 branching, cadence flag, extraction arcs │ High — two phases with different rules │
  └─────────────────────┴────────────────────────────────────────────────────────────┴────────────────────────────────────────┘                                                                                                                                
                  
  Pro: Each agent has a narrow, testable scope. You can validate one algorithm's visuals completely before moving to the next. The prompt for each agent is focused — no risk of one algorithm's rules bleeding into another.                                  
                  
  Con: Four agents to maintain. Some shared concerns (sprite identity, z-ordering, easing curves) get duplicated or need a shared base.                                                                                                                        
                  
  Option: One animation agent with per-algorithm contracts                                                                                                                                                                                                     
                  
  A single agent that understands the animation framework (sprites, easing, z-order, timing) and receives a structured contract per algorithm — not prose, but a table-driven spec it can execute against.                                                     
                  
  Pro: Shared rendering logic stays in one place. Closer to how the actual code will be structured (one View module with algorithm-specific renderers).                                                                                                        
                  
  Con: The agent's context gets heavy. This is essentially what the current specs try to do, and the traps show it's hard to get right in one pass.                                                                                                            
                  
  My honest assessment                                                                                                                                                                                                                                         
                  
  Don't start over. Don't patch the specs either. Instead:                                                                                                                                                                                                     
                  
  1. Keep the Model/Controller specs as-is. They work.                                                                                                                                                                                                         
  2. Create per-algorithm animation contracts — not prose documents, but structured tables that serve as both the spec and the agent prompt. Each contract is a self-contained document that says: "Given these tick types, here is the exact rendering
  behavior, state machine, and timing for this algorithm." Think of them as the 11_VIEW_CONTRACTS.md idea from Option B, but split per algorithm.                                                                                                              
  3. Build a phased animation agent workflow — either one agent with four contracts or four specialized agents. The contracts replace the scattered information across docs 03, 05, 06, and 10.
                                                                                                                                                                                                                                                               
  The key shift: instead of writing specs that a general agent interprets, you write contracts that an animation agent executes. The contract format should be tables and state machines, not paragraphs.                                                      
                                                                                                                                                                                                                                                               
  What this means practically                                                                                                                                                                                                                                  
                  
  The nine traps become rows in contract tables rather than gotchas buried in prose. For example, Trap F (Selection Sort pointers) stops being a paragraph and becomes:                                                                                        
                  
  POINTER LIFECYCLE — Selection Sort                                                                                                                                                                                                                           
  | Tick    | State          | i_ptr | j_ptr | min_ptr | Rule                    |                                                                                                                                                                             
  |---------|----------------|-------|-------|---------|-------------------------|                                                                                                                                                                             
  | Scan T1 | j != min_idx   | show  | show  | show    | all three visible       |                                                                                                                                                                             
  | Scan T1 | j == min_idx   | show  | hide  | show    | min absorbs j           |                                                                                                                                                                             
  | Swap T2 | active         | hide  | hide  | show    | only min during swap    |                                                                                                                                                                             
  | Reset   | inter-pass     | move  | reset | reset   | i advances, j/min reset |                                                                                                                                                                             
                                                                                                                                                                                                                                                               
  An animation agent reading that table won't miss the coalescing rule. It can't — it's a row, not a buried sentence.                                                                                                                                          
                                                                                                                                                                                                                                                               
  ---                                                                                                                                                                                                                                                          
  You're not overcomplicating this. You identified that the real product is the animation, and the specs under-invested there. An animation agent with structured contracts is a cleaner solution than trying to make prose specs do a job they weren't
  designed for.                                                                                                                                                                                                                                                
               