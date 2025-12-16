(function () {
    // Tuning knobs
    const CONTRAST_SENS = 0.005;
    const BRIGHT_SENS = 0.003;
    const SAMPLE_TARGET = 5000;
    const P_LO = 0.02, P_HI = 0.98;

    const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));

    function sampleZ(z) {
        if (!Array.isArray(z) || z.length === 0) return [];
        const rows = z.length;
        const cols = Array.isArray(z[0]) ? z[0].length : 0;
        if (!cols) return [];

        const total = rows * cols;
        const stride = Math.max(1, Math.floor(Math.sqrt(total / SAMPLE_TARGET)));

        const out = [];
        for (let r = 0; r < rows; r += stride) {
            const row = z[r];
            if (!Array.isArray(row)) continue;
            for (let c = 0; c < cols; c += stride) {
                const v = row[c];
                if (Number.isFinite(v)) out.push(v);
            }
        }
        return out;
    }

    function percentile(sorted, p) {
        if (!sorted.length) return 0;
        const idx = (sorted.length - 1) * p;
        const lo = Math.floor(idx);
        const hi = Math.ceil(idx);
        if (lo === hi) return sorted[lo];
        const t = idx - lo;
        return sorted[lo] * (1 - t) + sorted[hi] * t;
    }

    function initState(gd) {
        if (gd._bcState) return gd._bcState;

        const trace = gd.data && gd.data[0];
        const z = trace && trace.z;
        const s = sampleZ(z);
        s.sort((a, b) => a - b);

        let baseMin = percentile(s, P_LO);
        let baseMax = percentile(s, P_HI);
        if (!(baseMax > baseMin)) { baseMin = 0; baseMax = 1; }

        const baseWidth = baseMax - baseMin;
        const state = {
            dragging: false,
            lastX: null,
            lastY: null,
            baseMin,
            baseMax,
            baseCenter: (baseMin + baseMax) / 2,
            baseWidth,
            center: (baseMin + baseMax) / 2,
            width: baseWidth,
            minWidth: baseWidth / 2000,
            maxWidth: baseWidth * 50
        };

        gd._bcState = state;
        return state;
    }

    function applyWindow(gd) {
        const st = gd._bcState;
        const half = st.width / 2;
        const zmin = st.center - half;
        const zmax = st.center + half;
        Plotly.restyle(gd, { zmin: [zmin], zmax: [zmax] }, [0]);
    }

    function resetWindow(gd) {
        const st = initState(gd);
        st.center = st.baseCenter;
        st.width = st.baseWidth;
        applyWindow(gd);
    }

    // NEW: Get the paired FT graph for a given raw graph
    function getPairedFtGraph(rawGraphId) {
        // Extract card number from raw-graph-N
        const match = rawGraphId.match(/raw-graph-(\d+)/);
        if (!match) return null;
        
        const cardId = match[1];
        
        // Find the FT graph with matching card_id
        const ftGraphs = document.querySelectorAll('[id*="ft-graph"]');
        for (let ftGraph of ftGraphs) {
            const ftId = ftGraph.id;
            if (ftId.includes(`"card_id":${cardId}`) || ftId.includes(`'card_id':${cardId}`)) {
                return ftGraph.querySelector('.js-plotly-plot');
            }
        }
        return null;
    }

    // NEW: Sync brightness/contrast from raw to FT
    function syncToFtGraph(rawGd) {
        const rawState = rawGd._bcState;
        if (!rawState) return;

        const ftGd = getPairedFtGraph(rawGd.parentElement.id);
        if (!ftGd) return;

        // Initialize FT graph state if needed
        const ftState = initState(ftGd);
        
        // Calculate the adjustment ratios from raw graph
        const centerOffset = rawState.center - rawState.baseCenter;
        const widthRatio = rawState.width / rawState.baseWidth;

        // Apply the same relative adjustments to FT graph
        ftState.center = ftState.baseCenter + (centerOffset * (ftState.baseWidth / rawState.baseWidth));
        ftState.width = ftState.baseWidth * widthRatio;
        
        // Clamp to valid range
        ftState.width = clamp(ftState.width, ftState.minWidth, ftState.maxWidth);

        applyWindow(ftGd);
    }

    function attachToGraphDiv(gd) {
        if (!gd || gd.dataset.bcAttached === "1") return;
        gd.dataset.bcAttached = "1";

        gd.style.touchAction = "none";
        gd.style.cursor = "grab";

        gd.addEventListener("pointerdown", (e) => {
            const st = initState(gd);
            st.dragging = true;
            st.lastX = e.clientX;
            st.lastY = e.clientY;
            gd.setPointerCapture?.(e.pointerId);
            gd.style.cursor = "grabbing";
        });

        gd.addEventListener("pointermove", (e) => {
            const st = initState(gd);
            if (!st.dragging) return;

            const dx = e.clientX - st.lastX;
            const dy = e.clientY - st.lastY;
            st.lastX = e.clientX;
            st.lastY = e.clientY;

            const factor = Math.exp(dx * CONTRAST_SENS);
            st.width = clamp(st.width * factor, st.minWidth, st.maxWidth);
            st.center += (-dy) * (st.width * BRIGHT_SENS);

            applyWindow(gd);
            
            // NEW: Sync to paired FT graph
            syncToFtGraph(gd);
        });

        const stopDrag = () => {
            const st = initState(gd);
            st.dragging = false;
            gd.style.cursor = "grab";
        };

        gd.addEventListener("pointerup", stopDrag);
        gd.addEventListener("pointercancel", stopDrag);
        gd.addEventListener("pointerleave", stopDrag);

        gd.addEventListener("dblclick", (e) => {
            e.preventDefault();
            resetWindow(gd);
            
            // NEW: Also reset paired FT graph
            const ftGd = getPairedFtGraph(gd.parentElement.id);
            if (ftGd) {
                resetWindow(ftGd);
            }
        });
    }

    function scanAndAttach() {
        // Attach to input raw graphs (1-4)
        for (let i = 1; i <= 4; i++) {
            const outer = document.getElementById(`raw-graph-${i}`);
            if (!outer) continue;

            const gd = outer.querySelector(".js-plotly-plot");
            if (gd) attachToGraphDiv(gd);
        }

        // Attach to output viewports (viewport1 and viewport2)
        const outputViewports = ['output-viewport1', 'output-viewport2'];
        for (let viewportId of outputViewports) {
            const viewport = document.getElementById(viewportId);
            if (!viewport) continue;

            // Find the Plotly graph div inside the viewport
            const gd = viewport.querySelector(".js-plotly-plot");
            if (gd) attachToGraphDiv(gd);
        }
    }

    document.addEventListener("DOMContentLoaded", scanAndAttach);
    new MutationObserver(scanAndAttach).observe(document.body, { childList: true, subtree: true });
})();