// Given 3 collinear points p, q, r, the function checks if point q lies on line segment 'pr'
const on_segment = (p, q, r) =>  {
	if (q.x <= Math.max(p.x, r.x) && q.x >= Math.min(p.x, r.x) && 
		q.y <= Math.max(p.y, r.y) && q.y >= Math.min(p.y, r.y))
	    return true
	return false
}

const sign = (val) => {
    if (val == 0)
        return 0
    return val > 0 ? 1 : -1
}

// To find orientation of ordered triplet (p, q, r).
// The function returns following values
// 0 --> p, q and r are collinear
// x > 0 --> Clockwise
// x < 0 --> Counterclockwise
const orientation = (p, q, r) => {
	return  (q.y - p.y) * (r.x - q.x) -
		    (q.x - p.x) * (r.y - q.y)
}

// Returns true if line segment 'p1q1' and 'p2q2' intersect.
const do_intersect = (p1, q1, p2, q2) => {
	// Find the four orientations needed for general and
	// special cases
	let so1 = sign(orientation(p1, q1, p2))
	let so2 = sign(orientation(p1, q1, q2))
	let so3 = sign(orientation(p2, q2, p1))
	let so4 = sign(orientation(p2, q2, q1))

	// General case
	if (so1 != so2 && so3 != so4)
		return true
	// Special Cases 
	// p1, q1 and p2 are collinear and p2 lies on segment p1q1
	if (so1 == 0 && on_segment(p1, p2, q1))
        return true
	// p1, q1 and q2 are collinear and q2 lies on segment p1q1
	if (so2 == 0 && on_segment(p1, q2, q1))
        return true
	// p2, q2 and p1 are collinear and p1 lies on segment p2q2
	if (so3 == 0 && on_segment(p2, p1, q2))
        return true
	// p2, q2 and q1 are collinear and q1 lies on segment p2q2
	if (so4 == 0 && on_segment(p2, q1, q2))
        return true
	return false // Doesn't fall in any of the above cases
}

// Check if a new edge added to a polygon intersects with any other edge
const check_intersection_polygon = (poly, new_point) => {
    if (poly.length < 2)
        return false
    let new_edge = [ poly.at(-1), new_point ]
    for (let i = 0; i < poly.length - 2; i++) {
        if (do_intersect(poly[i], poly[i + 1], new_edge[0], new_edge[1]))
            return true
    }
    return false
}

export {
    check_intersection_polygon
}