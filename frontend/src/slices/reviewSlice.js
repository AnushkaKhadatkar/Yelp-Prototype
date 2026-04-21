import { createAsyncThunk, createSlice } from '@reduxjs/toolkit'
import { createReview, deleteReview, updateReview } from '../services/api'

export const submitReview = createAsyncThunk(
  'review/submitReview',
  async ({ restaurantId, payload }, { rejectWithValue }) => {
    try {
      const res = await createReview(restaurantId, payload)
      return {
        restaurantId: Number(restaurantId),
        reviewId: res?.data?.review_id ?? null,
        eventId: res?.data?.eventId ?? null,
      }
    } catch (err) {
      return rejectWithValue(err?.response?.data?.detail || 'Failed to submit review.')
    }
  }
)

export const updateReviewStatus = createAsyncThunk(
  'review/updateReviewStatus',
  async ({ reviewId, payload }, { rejectWithValue }) => {
    try {
      const res = await updateReview(reviewId, payload)
      return {
        reviewId: Number(reviewId),
        eventId: res?.data?.eventId ?? null,
      }
    } catch (err) {
      return rejectWithValue(err?.response?.data?.detail || 'Failed to update review.')
    }
  }
)

export const removeReview = createAsyncThunk(
  'review/deleteReview',
  async (reviewId, { rejectWithValue }) => {
    try {
      const res = await deleteReview(reviewId)
      return {
        reviewId: Number(reviewId),
        eventId: res?.data?.eventId ?? null,
      }
    } catch (err) {
      return rejectWithValue(err?.response?.data?.detail || 'Failed to delete review.')
    }
  }
)

const initialState = {
  submitting: false,
  updating: false,
  deleting: false,
  submitError: null,
  updateError: null,
  deleteError: null,
  lastSubmittedReviewId: null,
  lastUpdatedReviewId: null,
  lastDeletedReviewId: null,
}

export const reviewSlice = createSlice({
  name: 'review',
  initialState,
  reducers: {
    clearReviewErrors: (state) => {
      state.submitError = null
      state.updateError = null
      state.deleteError = null
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(submitReview.pending, (state) => {
        state.submitting = true
        state.submitError = null
      })
      .addCase(submitReview.fulfilled, (state, action) => {
        state.submitting = false
        state.lastSubmittedReviewId = action.payload.reviewId
      })
      .addCase(submitReview.rejected, (state, action) => {
        state.submitting = false
        state.submitError =
          typeof action.payload === 'string' ? action.payload : 'Failed to submit review.'
      })
      .addCase(updateReviewStatus.pending, (state) => {
        state.updating = true
        state.updateError = null
      })
      .addCase(updateReviewStatus.fulfilled, (state, action) => {
        state.updating = false
        state.lastUpdatedReviewId = action.payload.reviewId
      })
      .addCase(updateReviewStatus.rejected, (state, action) => {
        state.updating = false
        state.updateError =
          typeof action.payload === 'string' ? action.payload : 'Failed to update review.'
      })
      .addCase(removeReview.pending, (state) => {
        state.deleting = true
        state.deleteError = null
      })
      .addCase(removeReview.fulfilled, (state, action) => {
        state.deleting = false
        state.lastDeletedReviewId = action.payload.reviewId
      })
      .addCase(removeReview.rejected, (state, action) => {
        state.deleting = false
        state.deleteError =
          typeof action.payload === 'string' ? action.payload : 'Failed to delete review.'
      })
  },
})

export const { clearReviewErrors } = reviewSlice.actions
export default reviewSlice.reducer
