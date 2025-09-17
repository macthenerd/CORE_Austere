// src/utils/textHighlight.js

/**
 * Highlight search terms in text with context
 */

export const highlightText = (text, searchTerms, options = {}) => {
  const {
    highlightClass = 'highlight',
    contextLength = 100,
    maxSnippets = 3,
    caseSensitive = false
  } = options;

  if (!text || !searchTerms) return text;

  // Convert search terms to array and clean
  const terms = Array.isArray(searchTerms) 
    ? searchTerms 
    : searchTerms.split(/\s+/).filter(term => term.length > 2); // Only highlight terms > 2 chars

  if (terms.length === 0) return text;

  // Create regex pattern for all terms
  const flags = caseSensitive ? 'g' : 'gi';
  const pattern = terms.map(term => 
    term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') // Escape special regex chars
  ).join('|');
  
  const regex = new RegExp(`(${pattern})`, flags);

  // Split text into parts and highlight matches
  const parts = text.split(regex);
  
  return parts.map((part, index) => {
    const isMatch = regex.test(part);
    if (isMatch) {
      return `<mark class="${highlightClass}">${part}</mark>`;
    }
    return part;
  }).join('');
};

export const getContextSnippets = (text, searchTerms, options = {}) => {
  const {
    contextLength = 150,
    maxSnippets = 3,
    caseSensitive = false
  } = options;

  if (!text || !searchTerms) return [text.substring(0, 200) + '...'];

  const terms = Array.isArray(searchTerms) 
    ? searchTerms 
    : searchTerms.split(/\s+/).filter(term => term.length > 2);

  if (terms.length === 0) return [text.substring(0, 200) + '...'];

  // Find all match positions
  const matches = [];
  const flags = caseSensitive ? 'gi' : 'gi';
  
  terms.forEach(term => {
    const regex = new RegExp(term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), flags);
    let match;
    while ((match = regex.exec(text)) !== null) {
      matches.push({
        start: match.index,
        end: match.index + match[0].length,
        term: match[0]
      });
    }
  });

  if (matches.length === 0) {
    return [text.substring(0, 200) + '...'];
  }

  // Sort matches by position
  matches.sort((a, b) => a.start - b.start);

  // Create context snippets around matches
  const snippets = [];
  let lastEnd = 0;

  matches.slice(0, maxSnippets * 2).forEach(match => {
    // Skip if this match is too close to the previous one
    if (match.start < lastEnd) return;

    const start = Math.max(0, match.start - contextLength / 2);
    const end = Math.min(text.length, match.end + contextLength / 2);
    
    let snippet = text.substring(start, end);
    
    // Add ellipsis if we're not at the start/end
    if (start > 0) snippet = '...' + snippet;
    if (end < text.length) snippet = snippet + '...';

    snippets.push(snippet);
    lastEnd = end;

    if (snippets.length >= maxSnippets) return;
  });

  return snippets.length > 0 ? snippets : [text.substring(0, 200) + '...'];
};

export const highlightSnippets = (snippets, searchTerms, highlightClass = 'highlight') => {
  return snippets.map(snippet => highlightText(snippet, searchTerms, { highlightClass }));
};
