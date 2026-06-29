// Checks if the response mentions the expected OKF file path.
// Proxy for "did Claude know where to look?".
module.exports = (output, context) => {
  const expected = context.vars.expected_file || '';
  const mentioned = output.toLowerCase().includes(expected.toLowerCase());
  return {
    pass: mentioned,
    score: mentioned ? 1 : 0,
    reason: mentioned
      ? `Response references expected file: ${expected}`
      : `Response does not mention ${expected}`,
  };
};
