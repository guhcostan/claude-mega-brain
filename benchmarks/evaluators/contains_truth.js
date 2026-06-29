// Checks if the response contains the ground truth string (case-insensitive).
// Simple correctness signal — not a substitute for semantic eval.
module.exports = (output, context) => {
  const truth = context.vars.ground_truth || '';
  const correct = output.toLowerCase().includes(truth.toLowerCase());
  return {
    pass: correct,
    score: correct ? 1 : 0,
    reason: correct
      ? `Response contains ground truth: "${truth}"`
      : `Response missing ground truth: "${truth}"`,
  };
};
