var Course = require("../models/course");
var Comment = require("../models/comment");
var Review = require("../models/review");

// all the middleare goes here
var middlewareObj = {};

middlewareObj.checkCourseOwnership = function(req, res, next) {
    if(req.isAuthenticated()){
        Course.findById(req.params.id, function(err, foundCourse){
            if(err){
                req.flash("error", "Courses not found!");
                res.redirect("back");
                }  else {
                    // does user own the course?
                    if(foundCourse.author.id.equals(req.user._id) || req.user.isAdmin) {
                    next();
                    } else {
                        req.flash("error", "You don't have acccess to do that!");
                        res.redirect("back");
                        }
                    }
                });
    } else {
        req.flash("error", "You don't have acccess to do that!");
        res.redirect("back");
        }
};

middlewareObj.checkCommentOwnership = function(req, res, next) {
    if(req.isAuthenticated()){
        Comment.findById(req.params.comment_id, function(err, foundComment){
            if(err){
                res.redirect("back");
                }  else {
                    // does user own the comment?
                    if(foundComment.author.id.equals(req.user._id) || req.user.isAdmin) {
                        next();
                    } else {
                        req.flash("error", "You don't have acccess to do that!");
                        res.redirect("back");
                        }
                    }
                });
    } else {
        req.flash("error", "Please log in first!");
        res.redirect("back");
        }
};

middlewareObj.checkReviewOwnership = function(req, res, next) {
    if(req.isAuthenticated()){
        Review.findById(req.params.review_id, function(err, foundReview){
            if(err || !foundReview){
                res.redirect("back");
            }  else {
                // does user own the comment?
                if(foundReview.author.id.equals(req.user._id)) {
                    next();
                } else {
                    req.flash("error", "You don't have permission to do that");
                    res.redirect("back");
                }
            }
        });
    } else {
        req.flash("error", "You need to be logged in to do that");
        res.redirect("back");
    }
};

middlewareObj.checkReviewExistence = function (req, res, next) {
    if (req.isAuthenticated()) {
        Course.findById(req.params.id).populate("reviews").exec(function (err, foundCourse) {
            if (err || !foundCourse) {
                req.flash("error", "Course not found.");
                res.redirect("back");
            } else {
                // check if req.user._id exists in foundCourse.reviews
                var foundUserReview = foundCourse.reviews.some(function (review) {
                    return review.author.id.equals(req.user._id);
                });
                if (foundUserReview) {
                    req.flash("error", "You already wrote a review.");
                    return res.redirect("back");
                }
                // if the review was not found, go to the next middleware
                next();
            }
        });
    } else {
        req.flash("error", "You need to login first.");
        res.redirect("back");
    }
};

middlewareObj.isLoggedIn = function(req, res, next){
    if(req.isAuthenticated()){
        return next();
    }
    req.flash("error", "Please log in first!");//before redirect
    res.redirect("/login");
};

module.exports = middlewareObj;