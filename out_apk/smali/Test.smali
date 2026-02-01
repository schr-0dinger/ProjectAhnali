.class public LTest;
.super Ljava/lang/Object;

.method public static main()V
    .locals 9

  :B0
    const/4 v0, 0
    # if c goto :B2 else :B3
  :B1
    return-void
  :B2
    move v1, v2
    const/4 v3, 1
    goto :B4
  :B3
    move v4, v5
    const/4 v6, 2
    goto :B4
  :B4
    move v7, v8
    goto :B1
.end method