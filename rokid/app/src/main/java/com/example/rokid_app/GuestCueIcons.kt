package com.example.rokid_app

// Generated from the shared SVG catalog by server/generate_android_cue_icons.py.
object GuestCueIcons {
    private val icons = mapOf(
        "king_room" to R.drawable.cue_king_room,
        "twin_room" to R.drawable.cue_twin_room,
        "suite" to R.drawable.cue_suite,
        "black_coffee" to R.drawable.cue_black_coffee,
        "green_tea" to R.drawable.cue_green_tea,
        "still_water" to R.drawable.cue_still_water,
        "vegetarian" to R.drawable.cue_vegetarian,
        "smoking_room" to R.drawable.cue_smoking_room,
        "shellfish" to R.drawable.cue_shellfish,
        "peanut" to R.drawable.cue_peanut,
        "milk" to R.drawable.cue_milk,
        "egg" to R.drawable.cue_egg
    )
    private val markers = mapOf(
        "prefer" to R.drawable.cue_marker_prefer,
        "dislike" to R.drawable.cue_marker_dislike,
        "allergy" to R.drawable.cue_marker_allergy
    )
    fun icon(code: String): Int? = icons[code]
    fun marker(sentiment: String): Int? = markers[sentiment]
}
