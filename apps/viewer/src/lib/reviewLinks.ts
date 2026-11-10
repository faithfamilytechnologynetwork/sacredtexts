// Links to a review cell's page, `/review/cell/$cellId` (Spec 154).
//
// A cell id is `<run>:<model_id>:<question_id>`, so it carries `:` and has to be percent-encoded
// in a path segment. TanStack Router already does both halves: it encodes a path param with
// `encodeURIComponent` when it builds a link, and decodes the matched segment with
// `decodeURIComponent` before handing it to the page. Decoding again on read would corrupt any id
// containing `%`. So every link and every read goes through these helpers, which leave the
// encoding to the router:
//   • `cellLink(id)` is the props for a `<Link>` to the cell;
//   • `cellHref(id)` is the URL that link produces (for tests and anything outside a `<Link>`);
//   • `cellIdFromParam(param)` reads the route's param back as the cell id.

export const CELL_ROUTE = "/review/cell/$cellId" as const;

/** Props for a `<Link>` to a cell's page: `<Link {...cellLink(id)}>`. */
export function cellLink(cellId: string) {
  return { to: CELL_ROUTE, params: { cellId } } as const;
}

/** The URL of a cell's page: the same string the router builds for `cellLink(cellId)`. */
export function cellHref(cellId: string): string {
  return `/review/cell/${encodeURIComponent(cellId)}`;
}

/** The cell id in a matched `$cellId` param. The router has already decoded it once. */
export function cellIdFromParam(param: string): string {
  return param;
}
