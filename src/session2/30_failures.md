## 9. ⚠️ How this still fails

The graph, the gate and the ROI table do not make the system safe. Three
limits are worth leaving the room with.

### 9.1 A step cap is still mandatory

`max_steps` in Session 1 is `recursion_limit` here. The default (25) is a
number, not a policy. Set it from the longest *legitimate* trace you have
seen, plus a little, and alert when you hit it.
