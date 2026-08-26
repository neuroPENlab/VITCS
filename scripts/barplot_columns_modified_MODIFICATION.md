# `barplot_columns_modified.m` — how to reproduce this local modification

This repository does **not** include a modified copy of CANlab's `barplot_columns.m` (part of [CANlab Core Tools](https://github.com/canlab/CanlabCore)), to avoid redistributing a derivative of third-party licensed code. `fig02c_test_set_barplot.m` expects a locally modified copy, `barplot_columns_modified.m`, which you need to create yourself as follows.

## Steps

1. In your own installation of CANlab Core Tools (already required — see "Requirements" in the main README), locate `barplot_columns.m` and save a copy named `barplot_columns_modified.m` **in the same folder**, right next to the original.

2. **Rename the function.** In the function declaration line, rename `barplot_columns` to `barplot_columns_modified` (and update the corresponding `:Usage:` line in the help text if you want it to stay accurate).

3. **Drop the pre-R2014b (<8.4) XTickLabelRotation fallback (lines 499 - 504).** Find the block that sets the x-axis tick labels when a `names` argument is given — it checks `verLessThan('matlab','8.4')` and only applies `'XTickLabelRotation', 45` on the newer branch. Replace that whole `if/else` block with a single unconditional call that always sets `set(gca, 'XTickLabel', names, 'XTickLabelRotation', 45);`.

4. **Color the within-subject lines by classification outcome (lines 528 - 538).** Inside the `if dolines` block, there is a single line that draws one gray line per subject connecting all of that subject's condition values (`handles.parallel_line_han{j} = plot(xvalues_for_lines(j, :), dat(j, :), ...)`). Replace that one line with the loop below, which colors each subject's segment by the sign of the slope between the two conditions being plotted — **green** for a negative slope (pattern expression correctly drops from CS+ to CS-) and **red** for a positive slope (incorrect classification):

   ```matlab
   for s = 1:2:size(dat,2)-1 % s is the column (each violin plot)
       slope = dat(j, s+1) - dat(j, s);
       if slope < 0
           handles.parallel_line_han{j} = plot([xvalues_for_lines(j, s+1) xvalues_for_lines(j, s)], ...
               [dat(j, s+1) dat(j, s)], 'k', 'LineWidth', .5, 'Color', [[0 .6 0], 0.5]);
       elseif slope > 0
           handles.parallel_line_han{j} = plot([xvalues_for_lines(j, s+1) xvalues_for_lines(j, s)], ...
               [dat(j, s+1) dat(j, s)], 'k', 'LineWidth', .5, 'Color', [[1 0 0], 0.5]);
       else
           handles.parallel_line_han{j} = plot([xvalues_for_lines(j, s+1) xvalues_for_lines(j, s)], ...
               [dat(j, s+1) dat(j, s)], 'k', 'LineWidth', .5, 'Color', [[.7 .7 .7], 0.5]);
       end
   end
   ```

   This loop (and the color logic above) is original code, not part of CANlab's `barplot_columns.m`.

Everything else in the file is left exactly as in the original CANlab `barplot_columns.m`.
